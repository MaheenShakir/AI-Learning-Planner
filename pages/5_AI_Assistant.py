import streamlit as st

from src.ai_assistant import ask_gemini, build_tutor_instruction, get_api_key
from src.database import init_db, get_latest_goal

init_db()

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

st.title("🤖 AI Learning Assistant")

goal = get_latest_goal()
if not goal:
    st.warning("Please save a learning goal first on the Learning Goal page.")
    st.stop()

if not get_api_key():
    st.error("No API key found. Add GEMINI_API_KEY in your app's Secrets.")
    st.stop()

st.caption(f"Helping you with **{goal['goal']}** at **{goal['level']}** level.")

if "chat" not in st.session_state:
    st.session_state.chat = []

# ---------- Quick-action buttons ----------
quick_prompts = {
    "📚 Resources": "Recommend the best learning resources for my goal.",
    "✏️ Exercises": "Suggest practice exercises for my goal and level.",
    "💡 Project ideas": "Give me 3 project ideas for my goal and level.",
    "🧭 Where to start": "What should I learn first, and why?",
}
prompt = None
cols = st.columns(len(quick_prompts))
for col, (label, text) in zip(cols, quick_prompts.items()):
    if col.button(label, use_container_width=True):
        prompt = text

typed = st.chat_input("Ask me to explain a concept or help with a topic...")
if typed:
    prompt = typed

# ---------- Show earlier messages ----------
for message in st.session_state.chat:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------- Handle a new question ----------
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    recent = st.session_state.chat[-6:]
    history = "\n".join(f"{m['role']}: {m['content']}" for m in recent)
    full_prompt = f"Conversation so far:\n{history}\n\nuser: {prompt}" if history else prompt

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = ask_gemini(full_prompt, build_tutor_instruction(goal))
            except Exception as e:
                answer = f"Sorry, the AI request failed: {e}"
        st.markdown(answer)

    st.session_state.chat.append({"role": "user", "content": prompt})
    st.session_state.chat.append({"role": "assistant", "content": answer})
