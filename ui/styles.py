"""
styles.py
---------
Custom CSS injected into the Streamlit app. Design direction: an academic,
index-card aesthetic (paper background, ink-navy structure, a single
highlighter-yellow signature accent) rather than a generic dark AI-tool
look — fitting for a study companion built by and for university students.
"""

CUSTOM_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,500;0,600;0,700;1,500&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">

<style>
    :root {
        --paper: #F7F5F0;
        --paper-raised: #FFFFFF;
        --ink: #1B2A4A;
        --ink-soft: #5B6478;
        --hairline: #E4E0D6;
        --navy: #1B2A4A;
        --navy-soft: #2E4270;
        --highlighter: #F2C14E;
        --highlighter-soft: rgba(242, 193, 78, 0.45);
        --brick: #B23A32;
        --brick-bg: #FBEAE8;
        --forest: #2F6B3A;
        --forest-bg: #E9F3EA;
    }

    /* ---------- Global ---------- */
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--ink);
    }

    .stApp {
        background: var(--paper);
    }

    .main .block-container {
        padding-top: 2.2rem;
        padding-bottom: 3rem;
        max-width: 1080px;
    }

    h1, h2, h3, h4 { font-family: 'Lora', serif; color: var(--ink); }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background: var(--navy);
        border-right: 1px solid rgba(0,0,0,0.15);
    }
    section[data-testid="stSidebar"] * { color: #EDEFF5; }
    section[data-testid="stSidebar"] .stTextInput input {
        color: var(--ink);
    }

    /* Sidebar nav buttons styled as binder tabs */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div.stButton > button {
        width: 100%;
        text-align: left;
        background: transparent;
        border: none;
        border-left: 3px solid transparent;
        border-radius: 0 8px 8px 0;
        color: #C9CFE0;
        font-weight: 500;
        font-size: 0.93rem;
        padding: 0.55rem 0.9rem;
        margin-bottom: 2px;
        transition: all 0.15s ease;
    }
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div.stButton > button:hover {
        background: rgba(255,255,255,0.06);
        color: #FFFFFF;
        border-left: 3px solid var(--highlighter-soft);
    }
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div.stButton > button[kind="primary"] {
        background: rgba(242, 193, 78, 0.14);
        color: #FFFFFF;
        border-left: 3px solid var(--highlighter);
        font-weight: 700;
    }

    /* ---------- Brand header ---------- */
    .brand-header {
        display: flex;
        align-items: baseline;
        gap: 8px;
        margin-bottom: 0.1rem;
    }
    .brand-title {
        font-family: 'Lora', serif;
        font-size: 1.35rem;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.01em;
    }
    .brand-tagline {
        color: #9AA3BC;
        font-size: 0.78rem;
        margin-bottom: 1.4rem;
    }

    /* ---------- Signature: highlighter-marker text ---------- */
    .marker-highlight {
        background-image: linear-gradient(180deg, transparent 58%, var(--highlighter-soft) 58%, var(--highlighter-soft) 92%, transparent 92%);
        padding: 0 2px;
    }

    /* ---------- Section headers ---------- */
    .section-header {
        font-family: 'Lora', serif;
        font-size: 1.7rem;
        font-weight: 700;
        color: var(--ink);
        margin-bottom: 0.15rem;
        display: inline-block;
    }
    .section-subheader {
        color: var(--ink-soft);
        font-size: 0.93rem;
        margin-bottom: 1.5rem;
        margin-top: 0.3rem;
    }

    /* ---------- Stat / index cards ---------- */
    .stat-card {
        background: var(--paper-raised);
        border: 1px solid var(--hairline);
        border-left: 3px solid var(--navy);
        border-radius: 4px;
        padding: 1rem 1.3rem;
        box-shadow: 0 1px 3px rgba(27,42,74,0.06);
    }
    .stat-number {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.9rem;
        font-weight: 600;
        color: var(--ink);
    }
    .stat-label {
        color: var(--ink-soft);
        font-size: 0.8rem;
        margin-top: 2px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .content-card {
        background: var(--paper-raised);
        border: 1px solid var(--hairline);
        border-radius: 6px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(27,42,74,0.05);
    }

    .doc-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #EEF1F8;
        color: var(--navy-soft);
        border: 1px solid var(--hairline);
        border-radius: 4px;
        padding: 4px 12px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        margin: 3px 6px 3px 0;
    }

    /* ---------- Flashcard (literal index card) ---------- */
    .flashcard {
        background: var(--paper-raised);
        border: 1px solid var(--hairline);
        border-left: 4px solid var(--brick);
        border-radius: 4px;
        padding: 1.5rem;
        min-height: 130px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        font-size: 1.05rem;
        color: var(--ink);
        margin-bottom: 0.6rem;
        box-shadow: 0 1px 3px rgba(27,42,74,0.06);
    }
    .flashcard-label {
        text-transform: uppercase;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
        letter-spacing: 0.1em;
        color: var(--brick);
        font-weight: 600;
        margin-bottom: 6px;
        display: block;
    }

    /* ---------- Quiz ---------- */
    .quiz-question {
        font-family: 'Lora', serif;
        font-weight: 600;
        font-size: 1.08rem;
        margin-bottom: 0.6rem;
        color: var(--ink);
    }
    .explanation-box {
        background: #EEF1F8;
        border-left: 3px solid var(--navy);
        padding: 0.7rem 1rem;
        border-radius: 4px;
        margin-top: 0.6rem;
        font-size: 0.9rem;
        color: var(--ink-soft);
    }

    /* ---------- Chat ---------- */
    .source-tag {
        display: inline-block;
        background: #EEF1F8;
        color: var(--navy-soft);
        border-radius: 4px;
        padding: 2px 8px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        margin-right: 6px;
        margin-top: 4px;
    }

    /* ---------- Streamlit component overrides ---------- */
    div.stButton > button {
        border-radius: 6px;
        font-weight: 600;
        border: 1px solid var(--hairline);
    }
    .main div.stButton > button[kind="primary"] {
        background: var(--navy);
        color: #FFFFFF;
        border: none;
    }
    .main div.stButton > button[kind="primary"]:hover {
        background: var(--navy-soft);
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--hairline);
        border-radius: 6px;
        background: var(--paper-raised);
    }

    .stAlert {
        border-radius: 6px;
    }

    div[data-testid="stChatMessage"] {
        background: var(--paper-raised);
        border: 1px solid var(--hairline);
        border-radius: 8px;
    }

    hr { border-color: var(--hairline); }

    /* Slim scrollbar for a tidier feel */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-thumb { background: var(--hairline); border-radius: 4px; }
</style>
"""


def inject_custom_css(st):
    """Inject the shared CSS into the current Streamlit page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
