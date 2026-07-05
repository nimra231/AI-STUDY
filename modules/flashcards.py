"""
flashcards.py
-------------
Generates question/answer flashcards from the uploaded notes for
quick revision, returned as structured JSON for the UI to render as
flip-cards.
"""

from __future__ import annotations
import json
import re
from typing import Optional, List, Dict
from langchain_community.vectorstores import FAISS

from modules.rag_engine import get_llm, RAGError
from modules.vector_store import similarity_search, VectorStoreError


def _extract_json(raw_text: str):
    cleaned = re.sub(r"```(json)?", "", raw_text).strip()
    return json.loads(cleaned)


def generate_flashcards(
    store: Optional[FAISS],
    num_cards: int = 10,
    topic_hint: str = "",
) -> List[Dict]:
    """
    Generate flashcards shaped like: {"question": str, "answer": str}
    """
    if store is None:
        raise RAGError("Please upload study material first before generating flashcards.")

    query = topic_hint.strip() if topic_hint.strip() else "important definitions and concepts"

    try:
        chunks = similarity_search(store, query, k=10)
    except VectorStoreError as exc:
        raise RAGError(str(exc)) from exc

    if not chunks:
        raise RAGError("This is not available in your uploaded notes.")

    context = "\n\n---\n\n".join(doc.page_content for doc in chunks)

    prompt = f"""You are helping a student build revision flashcards. Using ONLY the
notes below, create exactly {num_cards} flashcards covering the most important
concepts, definitions, and facts.

Respond ONLY with valid JSON — a list of objects, no preamble, no markdown fences.
Schema:
[
  {{"question": "short, focused question", "answer": "concise, clear answer"}}
]

Notes:
{context}

JSON:"""

    try:
        llm = get_llm(temperature=0.4)
        response = llm.invoke(prompt)
        cards = _extract_json(response.content)
        if not isinstance(cards, list) or not cards:
            raise RAGError("The AI did not return any usable flashcards. Try again.")
        return cards
    except RAGError:
        raise
    except json.JSONDecodeError as exc:
        raise RAGError(f"The AI's flashcard response couldn't be parsed. Please try again. ({exc})") from exc
    except Exception as exc:
        raise RAGError(f"Failed to generate flashcards: {exc}") from exc
