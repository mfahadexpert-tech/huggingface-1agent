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
# Light ChatGPT-style frontend.
st.markdown(
    """
    <style>
        /* Main application background */
        html,
        body,
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"],
        section.main {
            background: #ffffff !important;
            color: #202123 !important;
        }

        .block-container {
            max-width: 900px;
            padding-top: 2rem;
            padding-bottom: 7rem;
        }

        /* Main heading card */
        .hero {
            padding: 2rem;
            margin-bottom: 1.5rem;
            border: 1px solid #d9d9e3;
            border-radius: 22px;
            background: linear-gradient(
                135deg,
                #ecfdf5,
                #ffffff 65%
            ) !important;
            box-shadow: 0 10px 32px rgba(0, 0, 0, 0.06);
        }

        .hero-badge {
            display: inline-block;
            padding: 0.35rem 0.75rem;
            margin-bottom: 0.8rem;
            color: #087f5b;
            background: #d1fae5;
            border: 1px solid #a7f3d0;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .hero h1 {
            margin: 0;
            color: #202123 !important;
            font-size: clamp(2rem, 5vw, 3.4rem);
            letter-spacing: -0.05em;
        }

        .hero p {
            max-width: 650px;
            margin: 0.7rem 0 0;
            color: #565869 !important;
            font-size: 1rem;
            line-height: 1.7;
        }

        /* First-message introduction */
        .empty-state {
            padding: 1.2rem;
            margin: 1rem 0;
            color: #565869 !important;
            text-align: center;
            border: 1px dashed #c5c5d2;
            border-radius: 18px;
            background: #f7f7f8 !important;
        }

        /* Conversation history cards */
        [data-testid="stChatMessage"] {
            padding: 1rem;
            margin: 0.8rem 0;
            border: 1px solid #d9d9e3 !important;
            border-radius: 18px;
            background: #f7f7f8 !important;
            color: #202123 !important;
            box-shadow: 0 3px 14px rgba(0, 0, 0, 0.04);
        }

        /* Conversation text */
        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] span,
        [data-testid="stChatMessage"] li,
        [data-testid="stChatMessage"] code,
        [data-testid="stChatMessage"] div {
            color: #202123 !important;
        }

        /* Source links */
        [data-testid="stChatMessage"] a {
            color: #087f5b !important;
            font-weight: 600;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: #f7f7f8 !important;
            border-right: 1px solid #d9d9e3 !important;
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4 {
            color: #202123;
        }

        /* Message input */
        [data-testid="stChatInput"] {
            background: #ffffff !important;
            border: 1px solid #10a37f !important;
            border-radius: 18px;
            box-shadow: 0 8px 28px rgba(0, 0, 0, 0.08);
        }

        [data-testid="stChatInput"]:focus-within {
            border-color: #087f5b !important;
            box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.15);
        }

        [data-testid="stChatInput"] textarea {
            color: #202123 !important;
            background: #ffffff !important;
        }

        /* Area behind the chat input */
        [data-testid="stBottom"] {
            background: #ffffff !important;
        }

        /* Buttons */
        .stButton > button {
            border-color: #10a37f;
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