import os
import time

import streamlit as st
from google import genai
from google.genai import types

# Models are tried in order. If one is busy, the next one is used.
MODELS = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite"]


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
    """Send a prompt to Gemini. Retry once per model, then try the next model."""
    api_key = get_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=30000),
    )
    config = types.GenerateContentConfig(system_instruction=system_instruction)

    last_error = None
    for model in MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model, contents=prompt, config=config
                )
                return response.text
            except Exception as e:
                last_error = e
                time.sleep(1.5)  # short pause before retrying
    raise last_error
