import streamlit as st
from openai import OpenAI

# Initialize OpenAI client (expects OPENAI_API_KEY in environment or Streamlit Secrets)
client = OpenAI()

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "model" not in st.session_state:
        st.session_state.model = "gpt-4"
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.9
    if "style" not in st.session_state:
        st.session_state.style = "Classic"
    if "kid_safe" not in st.session_state:
        st.session_state.kid_safe = True
    if "length" not in st.session_state:
        st.session_state.length = "Short"

def build_system_instructions(style: str, kid_safe: bool, length: str) -> str:
    style_map = {
        "Classic": "Tell classic, universally funny jokes.",
        "Dad Jokes": "Lean into groan-worthy dad jokes and wordplay.",
        "Puns": "Focus on clever, punchy puns.",
        "Nerdy": "Use light-hearted humor referencing science, tech, and math.",
    }
    safety = "Keep it clean, friendly, and non-offensive." if kid_safe else "Stay witty but still avoid hate, harassment, or NSFW content."
    len_map = {
        "Short": "Keep jokes concise: 1-3 lines.",
        "Medium": "Keep jokes brief: up to 5 lines.",
        "One-liner": "Prefer one-liner jokes."
    }
    return (
        f"You are JokeBot, a friendly comedian. "
        f"{style_map.get(style, 'Tell classic, universally funny jokes.')} "
        f"{safety} "
        f"{len_map.get(length, 'Keep jokes concise: 1-3 lines.')} "
        f"If the user gives a topic, craft a joke about it. "
        f"If asked to explain, provide a brief, light explanation. "
        f"Avoid repeating jokes in the same conversation."
    )

def build_api_messages(user_and_assistant_history, style, kid_safe, length):
    # Requirement: include system "You are a helpful assistant."
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    # Additional system instruction to specialize the bot
    messages.append({"role": "system", "content": build_system_instructions(style, kid_safe, length)})
    # Add conversation history (exclude system messages from UI history; we only store user/assistant)
    messages.extend(user_and_assistant_history)
    return messages

def get_completion(model: str, messages, temperature: float):
    response = client.chat.completions.create(
        model=model,  # "gpt-4" or "gpt-3.5-turbo"
        messages=messages
    )
    return response.choices[0].message.content

def render_sidebar():
    with st.sidebar:
        st.header("JokeBot Settings")
        st.session_state.model = st.selectbox(
            "Model",
            options=["gpt-4", "gpt-3.5-turbo"],
            index=0 if st.session_state.model == "gpt-4" else 1,
            help="gpt-4 is generally funnier and more capable; gpt-3.5-turbo is faster and cheaper."
        )
        st.session_state.temperature = st.slider(
            "Creativity",
            0.0, 1.0, st.session_state.temperature, 0.1,
            help="Higher = more creative (and potentially more random)."
        )
        st.session_state.style = st.selectbox(
            "Style",
            options=["Classic", "Dad Jokes", "Puns", "Nerdy"],
            index=["Classic", "Dad Jokes", "Puns", "Nerdy"].index(st.session_state.style)
        )
        st.session_state.length = st.selectbox(
            "Length",
            options=["Short", "Medium", "One-liner"],
            index=["Short", "Medium", "One-liner"].index(st.session_state.length)
        )
        st.session_state.kid_safe = st.checkbox(
            "Kid-safe mode",
            value=st.session_state.kid_safe,
            help="Keep jokes clean and family-friendly."
        )

        st.markdown("---")
        if st.button("New Chat"):
            st.session_state.messages = []
            st.experimental_rerun()

        st.markdown("Tip: Set the OPENAI_API_KEY environment variable before running the app.")

def render_chat():
    st.title("JokeBot 🤖🎤")
    st.caption("A lighthearted chatbot that tells clean, witty jokes on any topic.")

    # Render existing chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Quick prompts
    cols = st.columns(4)
    quick_prompts = [
        "Tell me a dad joke.",
        "Make a pun about cats.",
        "A nerdy joke about Python.",
        "A one-liner about coffee."
    ]
    for i, prompt in enumerate(quick_prompts):
        if cols[i].button(prompt):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.experimental_rerun()

    # Chat input
    user_input = st.chat_input("Ask for a joke or give a topic (e.g., 'tell a joke about bananas').")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            try:
                api_messages = build_api_messages(
                    user_and_assistant_history=st.session_state.messages,
                    style=st.session_state.style,
                    kid_safe=st.session_state.kid_safe,
                    length=st.session_state.length
                )
                reply = get_completion(
                    model=st.session_state.model,
                    messages=api_messages,
                    temperature=st.session_state.temperature
                )
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error("There was an error generating a joke. Please check your API key and try again.")
                st.stop()

def main():
    st.set_page_config(page_title="JokeBot", page_icon="🎤", layout="centered")
    init_session_state()
    render_sidebar()
    render_chat()

if __name__ == "__main__":
    main()