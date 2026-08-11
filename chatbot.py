from providers.huggingface_provider import HuggingFaceProvider


SYSTEM_PROMPT = """
You are a helpful AI assistant with access to a web-search tool.

Use the search_web tool when:
- The user asks for current, recent, or changing information.
- The user asks about news, prices, schedules, releases, or events.
- You are uncertain whether your existing knowledge is accurate.
- The user explicitly asks you to search the web.

Do not search when:
- The user asks for creative writing.
- The question can be answered reliably without current information.
- The user asks you not to search.

When you use web search:
- Base your factual claims on the returned search results.
- Include clickable Markdown source links.
- Use the format [Source title](https://example.com).
- Never invent a URL or source.
- Explain when the search results are insufficient.
- Remember that search snippets may not contain the full webpage.

Give accurate, clear, and concise answers.
""".strip()


class Chatbot:
    def __init__(self) -> None:
        self.provider = HuggingFaceProvider()
        self.reset()

    def reset(self) -> None:
        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

    def reply(self, user_message: str) -> str:
        self.messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        try:
            answer = self.provider.chat(self.messages)
        except Exception:
            # Remove the failed user message from memory.
            self.messages.pop()
            raise

        self.messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        return answer