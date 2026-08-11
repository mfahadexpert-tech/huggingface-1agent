import json
import time
from typing import Any

from huggingface_hub import InferenceClient

from config import HF_MODEL, HF_TOKEN
from tools.web_search import SEARCH_WEB_TOOL, search_web


MAX_TOOL_ROUNDS = 8
MAX_RESPONSE_TOKENS = 2048
MAX_CALL_RETRIES = 5
RETRY_BACKOFF_BASE = 1.8


class HuggingFaceProvider:
    def __init__(self) -> None:
        """
        Create the Hugging Face API client.
        """

        self.model = HF_MODEL

        self.client = InferenceClient(
            provider="auto",
            api_key=HF_TOKEN,
        )

    def _create_completion(self, /, **kwargs: Any):
        """
        Call the HF client with retries for transient errors like 429.
        """
        attempt = 0
        while True:
            try:
                return self.client.chat.completions.create(**kwargs)
            except Exception as error:
                attempt += 1

                # Try to detect a transient 429 / overloaded error.
                status = None
                resp = getattr(error, "response", None)
                if resp is not None:
                    status = getattr(resp, "status_code", None)

                msg = str(error)
                is_transient = (
                    status == 429
                    or "429" in msg
                    or "Model busy" in msg
                    or "engine_overloaded" in msg
                )

                if not is_transient or attempt >= MAX_CALL_RETRIES:
                    raise

                backoff = RETRY_BACKOFF_BASE ** (attempt - 1)
                print(
                    f"Hugging Face request transient error (attempt {attempt}),"
                    f" retrying in {backoff:.1f}s: {error}"
                )
                time.sleep(backoff)

    def execute_tool(
        self,
        function_name: str,
        arguments: dict,
    ) -> dict[str, object]:
        """
        Find and execute a tool requested by the AI model.
        """

        if function_name == "search_web":
            query = arguments.get("query", "")
            max_results = arguments.get("max_results", 5)

            # This message appears in the VS Code terminal.
            print(f"DuckDuckGo search requested: {query}")

            return search_web(
                query=query,
                max_results=max_results,
            )

        return {
            "error": f"Unknown tool requested: {function_name}"
        }

    def chat(
        self,
        messages: list[dict[str, str]],
    ) -> str:
        """
        Generate an answer and allow the model to use tools.
        """

        # Copy the visible conversation.
        # Internal tool messages will only exist in this copy.
        working_messages = list(messages)

        for tool_round in range(MAX_TOOL_ROUNDS):
            print(
                f"Starting model request, "
                f"tool round {tool_round + 1}"
            )


            response = self._create_completion(
                model=self.model,
                messages=working_messages,
                tools=[SEARCH_WEB_TOOL],
                tool_choice="auto",
                max_tokens=MAX_RESPONSE_TOKENS,
            )

            # Support multiple response shapes returned by the HF client.
            choice = response.choices[0]
            response_message = getattr(choice, "message", None) or choice

            tool_calls = getattr(response_message, "tool_calls", None)

            # The model answered without requesting a tool.
            if not tool_calls:
                answer = getattr(response_message, "content", None) or getattr(response_message, "text", None)

                if answer:
                    return answer

                finish_reason = getattr(choice, "finish_reason", None)

                raise RuntimeError(
                    "The model returned an empty response. "
                    f"Finish reason: {finish_reason}. Model: {self.model}. "
                    f"Full response: {repr(response)[:2000]}"
                )

            # Store the model's request to use a tool.
            working_messages.append(response_message)

            # The model can request more than one tool.
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                raw_arguments = tool_call.function.arguments

                try:
                    if isinstance(raw_arguments, str):
                        arguments = json.loads(raw_arguments)
                    else:
                        arguments = raw_arguments

                    if not isinstance(arguments, dict):
                        raise TypeError(
                            "Tool arguments must be a dictionary."
                        )

                except (json.JSONDecodeError, TypeError) as error:
                    tool_result = {
                        "error": (
                            "The model supplied invalid tool "
                            f"arguments: {error}"
                        )
                    }

                else:
                    tool_result = self.execute_tool(
                        function_name=function_name,
                        arguments=arguments,
                    )

                # Return the tool result to the model.
                working_messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(
                            tool_result,
                            ensure_ascii=False,
                        ),
                    }
                )

        # If the model continues requesting tools after the
        # allowed number of rounds, keep tools enabled for the
        # final request so the model can finish search-based queries.
        final_response = self._create_completion(
            model=self.model,
            messages=working_messages,
            tools=[SEARCH_WEB_TOOL],
            tool_choice="auto",
            max_tokens=MAX_RESPONSE_TOKENS,
        )

        final_choice = final_response.choices[0]
        final_message = getattr(final_choice, "message", None) or final_choice

        final_tool_calls = getattr(final_message, "tool_calls", None)
        if final_tool_calls:
            raise RuntimeError(
                "The model still requested a tool call after the maximum "
                f"tool rounds ({MAX_TOOL_ROUNDS}). Tool calls: {final_tool_calls!r}. "
                f"Model: {self.model}."
            )

        final_answer = getattr(final_message, "content", None) or getattr(final_message, "text", None)

        if not final_answer:
            finish_reason = getattr(final_choice, "finish_reason", None)
            raise RuntimeError(
                "The model did not produce a final answer. "
                f"Finish reason: {finish_reason}. Model: {self.model}. "
                f"Full response: {repr(final_response)[:2000]}"
            )

        return final_answer