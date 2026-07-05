"""
rag_engine.py
-------------
Retrieval-Augmented Generation logic: given a user question, retrieve
the most relevant chunks from the FAISS store and ask the Gemini LLM
to answer strictly from that context. If the retrieved context does
not contain the answer, the model is instructed to say so explicitly
rather than hallucinate.
"""

from __future__ import annotations
from typing import List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS

from config import get_api_key, GEMINI_MODEL_NAME, RETRIEVER_TOP_K
from modules.vector_store import similarity_search, VectorStoreError

NOT_FOUND_PHRASE = "This is not available in your uploaded notes."


class RAGError(Exception):
    """Raised when the LLM call itself fails (bad key, network, quota, etc.)."""
    pass


def get_llm(temperature: float = 0.3) -> ChatGoogleGenerativeAI:
    """Create a configured Gemini chat model instance."""
    api_key = get_api_key()
    if not api_key:
        raise RAGError(
            "No Gemini API key found. Add one in the sidebar or in a .env file "
            "as GOOGLE_API_KEY."
        )
    try:
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL_NAME,
            google_api_key=api_key,
            temperature=temperature,
        )
    except Exception as exc:
        raise RAGError(f"Could not initialize the Gemini model: {exc}") from exc


def _format_context(chunks) -> str:
    """Join retrieved chunks into a single context block with source tags."""
    parts = []
    for doc in chunks:
        source = doc.metadata.get("source", "unknown")
        parts.append(f"[Source: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def answer_question(
    store: Optional[FAISS],
    question: str,
    chat_history: Optional[List[dict]] = None,
) -> dict:
    """
    Answer `question` using only the content retrieved from `store`.

    Returns a dict: {"answer": str, "sources": List[str], "found": bool}
    """
    if store is None:
        return {
            "answer": "Please upload at least one study document before asking questions.",
            "sources": [],
            "found": False,
        }

    try:
        retrieved_chunks = similarity_search(store, question, k=RETRIEVER_TOP_K)
    except VectorStoreError as exc:
        raise RAGError(str(exc)) from exc

    if not retrieved_chunks:
        return {"answer": NOT_FOUND_PHRASE, "sources": [], "found": False}

    context = _format_context(retrieved_chunks)
    sources = sorted({doc.metadata.get("source", "unknown") for doc in retrieved_chunks})

    history_snippet = ""
    if chat_history:
        recent = chat_history[-4:]  # keep prompt lean
        history_snippet = "\n".join(
            f"{turn['role'].capitalize()}: {turn['content']}" for turn in recent
        )

    system_prompt = f"""You are an AI Tutor that answers questions using ONLY the
study material provided in the context below. Do not use outside knowledge.

Rules:
- If the answer is fully or partially in the context, answer clearly and helpfully,
  in a friendly tutor tone, and cite which part of the notes it came from if useful.
- If the context does NOT contain the answer, reply EXACTLY with:
  "{NOT_FOUND_PHRASE}"
- Never make up information that isn't in the context.

Conversation so far:
{history_snippet}

Context from the student's uploaded notes:
{context}

Student's question: {question}

Answer:"""

    try:
        llm = get_llm(temperature=0.3)
        response = llm.invoke(system_prompt)
        answer_text = response.content.strip()
    except RAGError:
        raise
    except Exception as exc:
        raise RAGError(f"The AI Tutor failed to generate a response: {exc}") from exc

    found = NOT_FOUND_PHRASE.lower() not in answer_text.lower()
    return {
        "answer": answer_text,
        "sources": sources if found else [],
        "found": found,
    }
