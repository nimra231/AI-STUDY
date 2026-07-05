"""
app.py
------
Entry point for the StudyMate AI Streamlit application. Sets up the
page config, injects custom styling, renders the sidebar navigation
and API key input, then delegates rendering to the selected page in
ui/pages.py.

Run locally with:
    streamlit run app.py
"""

import streamlit as st

from config import APP_NAME, APP_TAGLINE, get_api_key
from ui.styles import inject_custom_css
from ui.pages import (
    render_dashboard,
    render_upload_notes,
    render_ai_tutor,
    render_summary,
    render_quiz,
    render_flashcards,
    render_study_planner,
)

# ---------------------------------------------------------------------------
# Page configuration (must be the first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=APP_NAME,
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css(st)

# ---------------------------------------------------------------------------
# Sidebar: branding, navigation, and API key
# ---------------------------------------------------------------------------
PAGES = {
    "🏠  Dashboard": render_dashboard,
    "📤  Upload Notes": render_upload_notes,
    "💬  AI Tutor": render_ai_tutor,
    "📝  Summary": render_summary,
    "🧠  Quiz Generator": render_quiz,
    "🗂️  Flashcards": render_flashcards,
    "📅  Study Planner": render_study_planner,
}

if "current_page" not in st.session_state:
    st.session_state["current_page"] = list(PAGES.keys())[0]

with st.sidebar:
    st.markdown(
        f'<div class="brand-header">'
        f'<span style="font-size:1.5rem;">📚</span>'
        f'<span class="brand-title">Study<span class="marker-highlight">Mate</span> AI</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="brand-tagline">{APP_TAGLINE}</div>', unsafe_allow_html=True)

    for page_name in PAGES:
        is_active = st.session_state["current_page"] == page_name
        if st.button(page_name, key=f"nav_{page_name}", type="primary" if is_active else "secondary"):
            st.session_state["current_page"] = page_name
            st.rerun()

    selected_page = st.session_state["current_page"]

    st.markdown("---")
    st.markdown("##### 🔑 Gemini API Key")
    api_key_input = st.text_input(
        "Enter your Gemini API key",
        type="password",
        value=st.session_state.get("google_api_key", ""),
        placeholder="AIza...",
        label_visibility="collapsed",
        help="Get a free key at aistudio.google.com/app/apikey",
    )
    st.session_state["google_api_key"] = api_key_input

    if get_api_key():
        st.success("API key connected", icon="✅")
    else:
        st.warning("Add a key to enable AI features", icon="⚠️")

    st.markdown("---")
    st.caption("Built with Streamlit, LangChain, FAISS & Gemini.")

# ---------------------------------------------------------------------------
# Route to the selected page
# ---------------------------------------------------------------------------
PAGES[selected_page](st)
