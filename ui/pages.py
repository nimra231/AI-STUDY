"""
ui/pages.py
-----------
Render functions for every page in the app. Each function takes the
active `st` (streamlit) module and reads/writes `st.session_state`
directly, keeping all UI logic separate from the document processing,
embedding, and generation modules.
"""

from __future__ import annotations
from datetime import datetime, date, timedelta

from modules import document_processor as docproc
from modules.vector_store import build_or_update_vector_store, remove_source_from_store, VectorStoreError
from modules.rag_engine import answer_question, RAGError
from modules.summarizer import generate_summary, SUMMARY_STYLES
from modules.quiz_generator import generate_quiz
from modules.flashcards import generate_flashcards
from modules.study_planner import generate_study_plan


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _ensure_session_state(st):
    defaults = {
        "documents": {},          # {filename: {"text": str, "uploaded_at": str, "chars": int}}
        "vector_store": None,
        "chat_history": [],
        "activity_log": [],       # list of {"time": str, "action": str}
        "google_api_key": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _log_activity(st, action: str):
    st.session_state["activity_log"].insert(
        0, {"time": datetime.now().strftime("%b %d, %I:%M %p"), "action": action}
    )
    st.session_state["activity_log"] = st.session_state["activity_log"][:15]


def _section_header(st, title: str, subtitle: str = ""):
    # Highlight the first word like a marker stroke — the page's signature accent.
    words = title.split(" ", 1)
    if len(words) == 2:
        styled_title = f'<span class="marker-highlight">{words[0]}</span> {words[1]}'
    else:
        styled_title = f'<span class="marker-highlight">{title}</span>'
    st.markdown(f'<div class="section-header">{styled_title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-subheader">{subtitle}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 1. Dashboard
# ---------------------------------------------------------------------------

def render_dashboard(st):
    _ensure_session_state(st)
    _section_header(st, "Dashboard", "An overview of your uploaded material and recent activity.")

    docs = st.session_state["documents"]
    total_chars = sum(d["chars"] for d in docs.values())
    total_chunks = 0
    if st.session_state["vector_store"] is not None:
        try:
            total_chunks = len(st.session_state["vector_store"].docstore._dict)
        except Exception:
            total_chunks = 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f'<div class="stat-card"><div class="stat-number">{len(docs)}</div>'
            f'<div class="stat-label">Documents Uploaded</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="stat-card"><div class="stat-number">{total_chunks}</div>'
            f'<div class="stat-label">Searchable Chunks</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div class="stat-card"><div class="stat-number">{len(st.session_state["chat_history"])}</div>'
            f'<div class="stat-label">Tutor Messages</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("#### Your Documents")
        if not docs:
            st.info("No documents uploaded yet. Head to **Upload Notes** to get started.")
        else:
            pills = "".join(f'<span class="doc-pill">📄 {name}</span>' for name in docs.keys())
            st.markdown(f'<div class="content-card">{pills}</div>', unsafe_allow_html=True)

    with right:
        st.markdown("#### Recent Activity")
        log = st.session_state["activity_log"]
        if not log:
            st.info("No activity yet.")
        else:
            items = "".join(
                f'<div style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.06);">'
                f'<span style="color:#9AA1B9;font-size:0.78rem;">{item["time"]}</span><br>{item["action"]}</div>'
                for item in log
            )
            st.markdown(f'<div class="content-card">{items}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 2. Upload Notes
# ---------------------------------------------------------------------------

def render_upload_notes(st):
    _ensure_session_state(st)
    _section_header(st, "Upload Notes", "Upload PDF, DOCX, PPTX, or TXT files to build your knowledge base.")

    uploaded_files = st.file_uploader(
        "Drag and drop or browse files",
        type=["pdf", "docx", "pptx", "txt"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        if st.button("Process & Embed Files", type="primary"):
            progress = st.progress(0, text="Starting...")
            errors = []
            for i, file in enumerate(uploaded_files):
                if file.name in st.session_state["documents"]:
                    progress.progress((i + 1) / len(uploaded_files), text=f"Skipping duplicate: {file.name}")
                    continue
                try:
                    progress.progress(i / len(uploaded_files), text=f"Reading {file.name}...")
                    file_bytes = file.read()
                    text = docproc.extract_text(file.name, file_bytes)

                    progress.progress((i + 0.5) / len(uploaded_files), text=f"Embedding {file.name}...")
                    st.session_state["vector_store"] = build_or_update_vector_store(
                        st.session_state["vector_store"], text, file.name
                    )

                    st.session_state["documents"][file.name] = {
                        "text": text,
                        "uploaded_at": datetime.now().strftime("%b %d, %Y %I:%M %p"),
                        "chars": len(text),
                    }
                    _log_activity(st, f"Uploaded and embedded **{file.name}**")
                except (docproc.DocumentProcessingError, VectorStoreError) as exc:
                    errors.append(f"{file.name}: {exc}")

                progress.progress((i + 1) / len(uploaded_files), text=f"Done with {file.name}")

            progress.empty()
            if errors:
                for err in errors:
                    st.error(err)
            else:
                st.success("All files processed and added to your knowledge base!")
            st.rerun()

    st.write("")
    st.markdown("#### Your Library")
    docs = st.session_state["documents"]

    if not docs:
        st.info("Nothing uploaded yet.")
        return

    search_term = st.text_input("🔍 Search your documents by filename", "")

    filtered = {
        name: data for name, data in docs.items()
        if search_term.lower() in name.lower()
    } if search_term else docs

    for name, data in filtered.items():
        with st.expander(f"📄 {name}  ·  {data['chars']:,} characters  ·  uploaded {data['uploaded_at']}"):
            st.text_area("Preview", data["text"][:1500] + ("..." if len(data["text"]) > 1500 else ""),
                         height=180, disabled=True, key=f"preview_{name}")
            if st.button(f"🗑️ Delete '{name}'", key=f"delete_{name}"):
                del st.session_state["documents"][name]
                st.session_state["vector_store"] = remove_source_from_store(
                    st.session_state["vector_store"], name
                )
                _log_activity(st, f"Deleted **{name}**")
                st.rerun()


# ---------------------------------------------------------------------------
# 3. AI Tutor
# ---------------------------------------------------------------------------

def render_ai_tutor(st):
    _ensure_session_state(st)
    _section_header(st, "AI Tutor", "Chat with your uploaded notes. Answers come only from your material.")

    if not st.session_state["documents"]:
        st.warning("Upload some notes first in **Upload Notes** to start chatting.")
        return

    for turn in st.session_state["chat_history"]:
        with st.chat_message(turn["role"]):
            st.markdown(turn["content"])
            if turn.get("sources"):
                tags = "".join(f'<span class="source-tag">📄 {s}</span>' for s in turn["sources"])
                st.markdown(tags, unsafe_allow_html=True)

    question = st.chat_input("Ask a question about your notes...")
    if question:
        st.session_state["chat_history"].append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking through your notes..."):
                try:
                    result = answer_question(
                        st.session_state["vector_store"], question, st.session_state["chat_history"]
                    )
                    st.markdown(result["answer"])
                    if result["sources"]:
                        tags = "".join(f'<span class="source-tag">📄 {s}</span>' for s in result["sources"])
                        st.markdown(tags, unsafe_allow_html=True)
                    st.session_state["chat_history"].append(
                        {"role": "assistant", "content": result["answer"], "sources": result["sources"]}
                    )
                    _log_activity(st, f"Asked the tutor: _{question[:50]}_")
                except RAGError as exc:
                    st.error(str(exc))


# ---------------------------------------------------------------------------
# 4. Summary
# ---------------------------------------------------------------------------

def render_summary(st):
    _ensure_session_state(st)
    _section_header(st, "Summary Generator", "Generate concise, detailed, or exam-focused summaries.")

    if not st.session_state["documents"]:
        st.warning("Upload some notes first in **Upload Notes**.")
        return

    col1, col2 = st.columns([1, 2])
    with col1:
        style = st.radio("Summary style", list(SUMMARY_STYLES.keys()))
    with col2:
        topic = st.text_input("Optional: focus on a specific topic", placeholder="e.g. Neural Networks")

    if st.button("Generate Summary", type="primary"):
        with st.spinner(f"Writing a {style.lower()} summary..."):
            try:
                summary = generate_summary(st.session_state["vector_store"], style, topic)
                st.markdown(f'<div class="content-card">{summary}</div>', unsafe_allow_html=True)
                _log_activity(st, f"Generated a **{style}** summary")
            except RAGError as exc:
                st.error(str(exc))


# ---------------------------------------------------------------------------
# 5. Quiz Generator
# ---------------------------------------------------------------------------

def render_quiz(st):
    _ensure_session_state(st)
    _section_header(st, "Quiz Generator", "Test yourself with auto-generated questions from your notes.")

    if not st.session_state["documents"]:
        st.warning("Upload some notes first in **Upload Notes**.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        q_types = st.multiselect(
            "Question types", ["MCQ", "True/False", "Short Answer"], default=["MCQ", "True/False"]
        )
    with col2:
        num_q = st.slider("Number of questions", 3, 15, 5)
    with col3:
        difficulty = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"], value="Medium")

    topic = st.text_input("Optional: focus on a specific topic", placeholder="e.g. Chapter 3", key="quiz_topic")

    if st.button("Generate Quiz", type="primary"):
        if not q_types:
            st.error("Select at least one question type.")
        else:
            with st.spinner("Building your quiz..."):
                try:
                    st.session_state["quiz_data"] = generate_quiz(
                        st.session_state["vector_store"], q_types, num_q, topic, difficulty
                    )
                    st.session_state["quiz_answers"] = {}
                    _log_activity(st, f"Generated a {num_q}-question quiz")
                except RAGError as exc:
                    st.error(str(exc))

    quiz_data = st.session_state.get("quiz_data")
    if quiz_data:
        st.write("")
        for i, q in enumerate(quiz_data):
            with st.container():
                st.markdown(f'<div class="content-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="quiz-question">Q{i+1}. {q["question"]}</div>', unsafe_allow_html=True)

                answer_key = f"quiz_ans_{i}"
                if q["type"] == "MCQ" and q.get("options"):
                    choice = st.radio("Choose one:", q["options"], key=answer_key, index=None)
                elif q["type"] == "True/False":
                    choice = st.radio("Choose one:", ["True", "False"], key=answer_key, index=None)
                else:
                    choice = st.text_input("Your answer:", key=answer_key)

                if st.button("Check Answer", key=f"check_{i}"):
                    is_correct = str(choice).strip().lower() == str(q["correct_answer"]).strip().lower()
                    if is_correct:
                        st.success(f"Correct! ✅")
                    else:
                        st.error(f"Not quite. Correct answer: **{q['correct_answer']}**")
                    st.markdown(
                        f'<div class="explanation-box">💡 {q.get("explanation", "")}</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 6. Flashcards
# ---------------------------------------------------------------------------

def render_flashcards(st):
    _ensure_session_state(st)
    _section_header(st, "Flashcards", "Quick question-and-answer cards for revision.")

    if not st.session_state["documents"]:
        st.warning("Upload some notes first in **Upload Notes**.")
        return

    col1, col2 = st.columns([1, 2])
    with col1:
        num_cards = st.slider("Number of flashcards", 5, 20, 10)
    with col2:
        topic = st.text_input("Optional: focus on a specific topic", placeholder="e.g. Key Definitions", key="fc_topic")

    if st.button("Generate Flashcards", type="primary"):
        with st.spinner("Creating your flashcards..."):
            try:
                st.session_state["flashcards_data"] = generate_flashcards(
                    st.session_state["vector_store"], num_cards, topic
                )
                st.session_state["flashcard_flipped"] = {}
                _log_activity(st, f"Generated {num_cards} flashcards")
            except RAGError as exc:
                st.error(str(exc))

    cards = st.session_state.get("flashcards_data")
    if cards:
        st.write("")
        cols = st.columns(2)
        for i, card in enumerate(cards):
            with cols[i % 2]:
                flipped = st.session_state.get("flashcard_flipped", {}).get(i, False)
                label = "Answer" if flipped else "Question"
                text = card["answer"] if flipped else card["question"]
                st.markdown(
                    f'<div class="flashcard"><div><span class="flashcard-label">{label}</span>{text}</div></div>',
                    unsafe_allow_html=True,
                )
                if st.button("🔄 Flip", key=f"flip_{i}"):
                    st.session_state.setdefault("flashcard_flipped", {})[i] = not flipped
                    st.rerun()


# ---------------------------------------------------------------------------
# 7. Study Planner
# ---------------------------------------------------------------------------

def render_study_planner(st):
    _ensure_session_state(st)
    _section_header(st, "Study Planner", "Build a day-by-day schedule based on your exam date and free time.")

    if not st.session_state["documents"]:
        st.warning("Upload some notes first in **Upload Notes**.")
        return

    col1, col2 = st.columns(2)
    with col1:
        exam_date = st.date_input("Exam date", value=date.today() + timedelta(days=7), min_value=date.today())
    with col2:
        daily_hours = st.slider("Available study hours per day", 0.5, 10.0, 2.0, step=0.5)

    if st.button("Generate Study Plan", type="primary"):
        with st.spinner("Building your personalized schedule..."):
            try:
                docs = st.session_state["documents"]
                sample_text = "\n".join(d["text"][:500] for d in docs.values())
                plan = generate_study_plan(list(docs.keys()), exam_date, daily_hours, sample_text)
                st.session_state["study_plan"] = plan
                _log_activity(st, "Generated a new study plan")
            except RAGError as exc:
                st.error(str(exc))

    plan = st.session_state.get("study_plan")
    if plan:
        st.write("")
        for entry in plan:
            with st.container():
                topics = ", ".join(entry.get("focus_topics", []))
                tasks = "".join(f"<li>{t}</li>" for t in entry.get("tasks", []))
                st.markdown(
                    f'<div class="content-card">'
                    f'<b>{entry.get("day", "")}</b> &nbsp;·&nbsp; {entry.get("hours", "")} hrs<br>'
                    f'<span style="color:#9AA1B9;">Focus: {topics}</span>'
                    f'<ul style="margin-top:8px;">{tasks}</ul>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
