import os

import streamlit as st
from google import genai
from google.genai import types

# Change the model name here if Google retires it.
MODEL_NAME = "gemini-3.8-flash"


def get_api_key():
    """Look for the key in Streamlit secrets first, then environment variables."""
    try:
        key = st.secrets["GEMINI_API_KEY"]
        if key:
            return key
    except Exception:
        pass  # no secrets file (e.g. running locally)
    return os.getenv("GEMINI_API_KEY")


def build_tutor_instruction(goal):
    """Tell the AI who it is and who it is talking to."""
    return (
        f"You are a friendly, encouraging tutor. The learner wants to learn "
        f"'{goal['goal']}', is at {goal['level']} level, and prefers "
        f"'{goal['learning_style']}' learning. Explain things in simple language, "
        f"keep answers focused and practical, and match the learner's level."
    )


def ask_gemini(prompt, system_instruction=None):
    """Send a prompt to Gemini and return the text answer."""
    api_key = get_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

        client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=30000),
    )
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system_instruction),
    )
    return response.text
