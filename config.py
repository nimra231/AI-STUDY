"""
config.py
---------
Centralized configuration for the AI Study Assistant.

Handles API key resolution (from .env, environment variable, or a
sidebar text input at runtime) and holds shared constants used across
every module so nothing is hard-coded in more than one place.
"""

import os
from dotenv import load_dotenv

# Load variables from a local .env file if one exists.
load_dotenv()

# ---------------------------------------------------------------------------
# General app constants
# ---------------------------------------------------------------------------
APP_NAME = "StudyMate AI"
APP_TAGLINE = "Your notes, turned into an AI study partner."

# Where uploaded files & the FAISS index are cached for the session.
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
VECTOR_STORE_DIR = os.path.join(DATA_DIR, "vector_store")
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

# Chunking parameters for the text splitter used before embedding.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Embedding model (runs locally via sentence-transformers, no API key needed).
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Gemini model used for all generation tasks (chat, summaries, quizzes...).
GEMINI_MODEL_NAME = "gemini-1.5-flash"

# How many chunks to retrieve from FAISS per query.
RETRIEVER_TOP_K = 4

SUPPORTED_EXTENSIONS = ["pdf", "docx", "pptx", "txt"]


def get_api_key() -> str | None:
    """
    Resolve the Google Gemini API key with the following priority:
    1. A key entered by the user in the current Streamlit session (sidebar).
    2. The GOOGLE_API_KEY environment variable / .env file.

    Returns None if no key is available anywhere.
    """
    try:
        import streamlit as st
        session_key = st.session_state.get("google_api_key")
        if session_key:
            return session_key
    except Exception:
        # config.py may be imported outside of a Streamlit runtime (e.g. tests)
        pass

    return os.environ.get("GOOGLE_API_KEY")
