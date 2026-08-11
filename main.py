from chatbot import Chatbot


def main() -> None:
    bot = Chatbot()

    print("Hugging Face chatbot")
    print("Commands: reset, exit")

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        command = user_input.lower()

        if command in {"exit", "quit"}:
            print("Goodbye!")
            break

        if command == "reset":
            bot.reset()
            print("Conversation memory cleared.")
            continue

        try:
            answer = bot.reply(user_input)
            print(f"\nAssistant: {answer}")
        except Exception as error:
            print(f"\nRequest failed: {error}")


if __name__ == "__main__":
    main()