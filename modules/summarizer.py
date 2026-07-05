"""
summarizer.py
-------------
Generates concise, detailed, or exam-focused summaries from the
uploaded notes, grounded strictly in retrieved content from FAISS.
"""

from __future__ import annotations
from typing import Optional
from langchain_community.vectorstores import FAISS

from modules.rag_engine import get_llm, RAGError
from modules.vector_store import similarity_search, VectorStoreError

SUMMARY_STYLES = {
    "Concise": (
        "Write a short, high-level summary in 5-8 bullet points covering only "
        "the most important ideas. Keep it tight and easy to skim."
    ),
    "Detailed": (
        "Write a thorough, well-structured summary with headings and sub-bullets "
        "that covers all key concepts, definitions, and relationships in depth."
    ),
    "Exam-Focused": (
        "Write a summary optimized for exam preparation: highlight definitions, "
        "formulas, key terms, likely exam points, and anything commonly tested. "
        "Use bold for critical terms and organize by topic."
    ),
}


def generate_summary(
    store: Optional[FAISS],
    style: str,
    topic_hint: str = "",
    max_chunks: int = 12,
) -> str:
    """
    Generate a summary of the uploaded material.

    `topic_hint` lets the user narrow the summary to a specific topic;
    if left blank, a broad sample of the document is summarized.
    """
    if store is None:
        return "Please upload study material first before generating a summary."

    if style not in SUMMARY_STYLES:
        style = "Concise"

    query = topic_hint.strip() if topic_hint.strip() else "overview of the main topics"

    try:
        chunks = similarity_search(store, query, k=max_chunks)
    except VectorStoreError as exc:
        raise RAGError(str(exc)) from exc

    if not chunks:
        return "This is not available in your uploaded notes."

    context = "\n\n---\n\n".join(doc.page_content for doc in chunks)

    prompt = f"""You are an expert study assistant. Using ONLY the notes below,
{SUMMARY_STYLES[style]}

Do not include information that isn't supported by the notes. If the notes are
insufficient to cover the requested topic, say so clearly.

Notes:
{context}

Summary:"""

    try:
        llm = get_llm(temperature=0.4)
        response = llm.invoke(prompt)
        return response.content.strip()
    except RAGError:
        raise
    except Exception as exc:
        raise RAGError(f"Failed to generate summary: {exc}") from exc
