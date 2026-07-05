"""
styles.py
---------
Custom CSS injected into the Streamlit app to give it a clean, modern,
professional look that goes beyond Streamlit's default styling.
"""

CUSTOM_CSS = """
<style>
    /* ---------- Global ---------- */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1100px;
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12162A 0%, #0E1117 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    section[data-testid="stSidebar"] .stRadio label {
        font-size: 0.95rem;
    }

    /* ---------- Brand header ---------- */
    .brand-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 0.25rem;
    }
    .brand-title {
        font-size: 1.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #7C8CFF, #4F6DF5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .brand-tagline {
        color: #9AA1B9;
        font-size: 0.82rem;
        margin-top: -6px;
        margin-bottom: 1.2rem;
    }

    /* ---------- Cards ---------- */
    .stat-card {
        background: linear-gradient(145deg, #161B29, #12172A);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 1.1rem 1.3rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    }
    .stat-number {
        font-size: 1.8rem;
        font-weight: 800;
        color: #EDEFFA;
    }
    .stat-label {
        color: #9AA1B9;
        font-size: 0.85rem;
        margin-top: 2px;
    }

    .content-card {
        background: #12172A;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1rem;
    }

    .doc-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(79,109,245,0.12);
        color: #A9B8FF;
        border: 1px solid rgba(79,109,245,0.35);
        border-radius: 999px;
        padding: 4px 12px;
        font-size: 0.8rem;
        margin: 3px 4px 3px 0;
    }

    /* ---------- Flashcard ---------- */
    .flashcard {
        background: linear-gradient(160deg, #1B2140, #12172A);
        border: 1px solid rgba(124,140,255,0.25);
        border-radius: 16px;
        padding: 1.5rem;
        min-height: 130px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        font-size: 1.05rem;
        color: #EDEFFA;
        margin-bottom: 0.6rem;
    }
    .flashcard-label {
        text-transform: uppercase;
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        color: #7C8CFF;
        font-weight: 700;
        margin-bottom: 6px;
        display: block;
    }

    /* ---------- Quiz ---------- */
    .quiz-question {
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 0.6rem;
        color: #EDEFFA;
    }
    .explanation-box {
        background: rgba(79,109,245,0.08);
        border-left: 3px solid #4F6DF5;
        padding: 0.7rem 1rem;
        border-radius: 8px;
        margin-top: 0.5rem;
        font-size: 0.9rem;
        color: #C7CCE6;
    }

    /* ---------- Chat ---------- */
    .source-tag {
        display: inline-block;
        background: rgba(255,255,255,0.06);
        color: #9AA1B9;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.72rem;
        margin-right: 6px;
    }

    /* ---------- Buttons ---------- */
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid rgba(255,255,255,0.08);
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #4F6DF5, #7C8CFF);
        border: none;
    }

    /* ---------- Section headers ---------- */
    .section-header {
        font-size: 1.5rem;
        font-weight: 800;
        color: #EDEFFA;
        margin-bottom: 0.2rem;
    }
    .section-subheader {
        color: #9AA1B9;
        font-size: 0.92rem;
        margin-bottom: 1.4rem;
    }

    /* ---------- Misc ---------- */
    hr {
        border-color: rgba(255,255,255,0.08);
    }
</style>
"""


def inject_custom_css(st):
    """Inject the shared CSS into the current Streamlit page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
