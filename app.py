import streamlit as st

from chatbot import Chatbot
from config import HF_MODEL, AVATAR_URL


# This must be the first Streamlit command.
st.set_page_config(
    page_title="Multi AI Assistant",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="expanded",
)


# Custom CSS adds visual styling that is not available
# through the standard Streamlit theme alone.
st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(
                    circle at 15% 10%,
                    rgba(124, 58, 237, 0.20),
                    transparent 30%
                ),
                radial-gradient(
                    circle at 85% 20%,
                    rgba(14, 165, 233, 0.14),
                    transparent 28%
                ),
                #080c18;
        }

        .block-container {
            max-width: 900px;
            padding-top: 2rem;
            padding-bottom: 7rem;
        }

        .hero {
            padding: 2rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 24px;
            background: linear-gradient(
                135deg,
                rgba(124, 58, 237, 0.18),
                rgba(14, 165, 233, 0.08)
            );
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
        }

        .hero-badge {
            display: inline-block;
            padding: 0.35rem 0.75rem;
            margin-bottom: 0.8rem;
            color: #c4b5fd;
            background: rgba(124, 58, 237, 0.16);
            border: 1px solid rgba(167, 139, 250, 0.25);
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .hero h1 {
            margin: 0;
            color: #f8fafc;
            font-size: clamp(2rem, 5vw, 3.4rem);
            letter-spacing: -0.05em;
        }

        .hero p {
            max-width: 650px;
            margin: 0.7rem 0 0;
            color: #b8c2d8;
            font-size: 1rem;
            line-height: 1.7;
        }

        .empty-state {
            padding: 1.2rem;
            margin: 1rem 0;
            color: #94a3b8;
            text-align: center;
            border: 1px dashed rgba(148, 163, 184, 0.25);
            border-radius: 18px;
            background: rgba(15, 23, 42, 0.35);
        }

        [data-testid="stChatMessage"] {
            padding: 1rem;
            margin: 0.8rem 0;
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 18px;
            background: rgba(15, 23, 42, 0.72);
            box-shadow: 0 8px 28px rgba(0, 0, 0, 0.14);
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(148, 163, 184, 0.13);
        }

        [data-testid="stChatInput"] {
            border: 1px solid rgba(139, 92, 246, 0.35);
            border-radius: 18px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.22);
        }

        @media (max-width: 640px) {
            .hero {
                padding: 1.3rem;
                border-radius: 18px;
            }

            .block-container {
                padding-top: 1rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_chatbot() -> None:
    """
    Create the chatbot only once for the current browser session.

    Streamlit reruns this file after every interaction.
    Session State prevents a new Chatbot from being created
    during each rerun.
    """
    if "bot" not in st.session_state:
        st.session_state.bot = Chatbot()


def clear_conversation() -> None:
    """Remove previous messages but keep the chatbot available."""
    st.session_state.bot.reset()


# Create or retrieve the chatbot stored in Session State.
initialize_chatbot()


# Sidebar
with st.sidebar:
    st.markdown("## ✦ Multi AI")

    st.caption(
        "A modular assistant powered by Hugging Face. "
        "Groq, Gemini, and web search can be added later."
    )

    st.divider()

    st.markdown("#### Current model")
    st.code(HF_MODEL, language=None)
    st.markdown("#### Available tools")
    st.success(
    "DuckDuckGo web search enabled",
    icon="🔎",
)

    st.markdown("#### Conversation")
    message_count = max(
        len(st.session_state.bot.messages) - 1,
        0,
    )
    st.metric("Messages", message_count)

    if st.button(
        "＋ Start new chat",
        use_container_width=True,
        type="primary",
    ):
        clear_conversation()
        st.rerun()

    st.divider()

    st.caption(
        "Conversation history currently lasts only for this "
        "browser session. Permanent memory can be added later."
    )


# Main header
st.markdown(
    """
    <section class="hero">
        <span class="hero-badge">Hugging Face Assistant</span>
        <h1>How can I help?</h1>
        <p>
            Ask questions, explore ideas, write content, or get
            help with Python. Your conversation stays available
            during the current browser session.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)


# Do not display the system prompt in the interface.
visible_messages = [
    message
    for message in st.session_state.bot.messages
    if message["role"] != "system"
]


# Show an introduction and example prompts before the first message.
if not visible_messages:
    st.markdown(
        """
        <div class="empty-state">
            Begin by writing a message below or selecting
            one of these example prompts.
        </div>
        """,
        unsafe_allow_html=True,
    )

    suggestions = [
        (
            "🐍 Explain Python",
            "Explain Python functions to a beginner with an example.",
        ),
        (
            "💡 Brainstorm",
            "Give me five useful AI project ideas for beginners.",
        ),
        (
            "✍️ Improve writing",
            "Help me write a professional project introduction.",
        ),
    ]

    suggestion_columns = st.columns(len(suggestions))

    for column, (label, suggestion) in zip(
        suggestion_columns,
        suggestions,
    ):
        with column:
            if st.button(label, use_container_width=True):
                st.session_state.pending_prompt = suggestion
                st.rerun()


# Display existing conversation messages.
for message in visible_messages:
    avatar = "🧑‍💻" if message["role"] == "user" else (AVATAR_URL or "✨")

    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


# Display the message input at the bottom of the page.
prompt = st.chat_input(
    "Message your AI assistant...",
    max_chars=4000,
)


# Use a suggestion as the prompt when a suggestion button is clicked.
if not prompt and "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")


# Process a new message.
if prompt:
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=(AVATAR_URL or "✨")):
        with st.spinner("Thinking..."):
            try:
                answer = st.session_state.bot.reply(prompt)
            except Exception as error:
                st.error(f"Request failed: {error}")
            else:
                st.markdown(answer)