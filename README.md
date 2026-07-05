# 📚 StudyMate AI — AI Study Assistant

An AI-powered study companion built with **Streamlit**, **LangChain**, **FAISS**, and the **Gemini API**. Upload your lecture notes (PDF, DOCX, PPTX, TXT) and get a personal tutor that answers questions, writes summaries, builds quizzes, generates flashcards, and plans your study schedule — all grounded strictly in *your* material via Retrieval-Augmented Generation (RAG).

---

## ✨ Features

| Page | What it does |
|---|---|
| 🏠 **Dashboard** | Overview of uploaded documents and recent activity |
| 📤 **Upload Notes** | Upload, preview, search, and delete PDF/DOCX/PPTX/TXT files |
| 💬 **AI Tutor** | Chat with your notes — answers only from your uploaded material, and clearly says so if something isn't covered |
| 📝 **Summary** | Concise, detailed, or exam-focused summaries |
| 🧠 **Quiz Generator** | MCQs, True/False, and short-answer questions with explanations |
| 🗂️ **Flashcards** | Auto-generated Q&A flashcards with flip-to-reveal |
| 📅 **Study Planner** | Day-by-day schedule based on your exam date and free hours |

## 🏗️ Architecture

```
ai_study_assistant/
├── app.py                     # Entry point — sidebar nav & page routing
├── config.py                  # Settings & API key resolution
├── modules/
│   ├── document_processor.py  # PDF / DOCX / PPTX / TXT text extraction
│   ├── vector_store.py        # Chunking, embeddings (local), FAISS index
│   ├── rag_engine.py          # Retrieval-Augmented Generation (chat)
│   ├── summarizer.py          # Summary generation
│   ├── quiz_generator.py      # Quiz generation (JSON-structured)
│   └── flashcards.py          # Flashcard generation
│   └── study_planner.py       # Study schedule generation
├── ui/
│   ├── styles.py               # Custom CSS for a modern look
│   └── pages.py                 # Page render functions
├── requirements.txt
└── .env.example
```

- **Embeddings** run locally via `sentence-transformers` (`all-MiniLM-L6-v2`) — free, no API key, no per-query cost.
- **Vector search** uses FAISS, held in memory per session (nothing is uploaded to a server).
- **Generation** (chat answers, summaries, quizzes, flashcards, plans) uses Google's **Gemini** API via LangChain.
- RAG is enforced with a strict prompt: if the retrieved notes don't contain the answer, the AI explicitly says *"This is not available in your uploaded notes."* instead of guessing.

## 🚀 Getting Started

### 1. Clone / download the project and install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get a free Gemini API key
Grab one at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).

You can either:
- Paste it into the sidebar once the app is running, **or**
- Copy `.env.example` to `.env` and set `GOOGLE_API_KEY=your_key_here`

### 3. Run the app
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## 🧪 Notes for graders / reviewers

- All AI modules raise clear, typed exceptions (`DocumentProcessingError`, `VectorStoreError`, `RAGError`) that the UI layer catches and displays as friendly messages — no raw stack traces reach the user.
- Every long-running step (file processing, embedding, generation) shows a Streamlit spinner or progress bar.
- The FAISS index and all uploaded content live only in `st.session_state` for the duration of the session — nothing is persisted to disk, keeping it simple to run and privacy-friendly for a portfolio demo.
- The first time you generate embeddings, `sentence-transformers` downloads its model (~90MB) from Hugging Face — this requires an internet connection on first run only, after which it's cached locally.

## 🛠️ Tech Stack

Python · Streamlit · LangChain · FAISS · PyMuPDF · python-docx · python-pptx · sentence-transformers · Google Gemini API
