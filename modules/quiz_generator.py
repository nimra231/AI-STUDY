"""
quiz_generator.py
------------------
Generates quiz questions (MCQ, True/False, Short Answer) from the
uploaded notes, with answers and explanations. The LLM is asked to
respond in strict JSON so the UI can render interactive quiz cards.
"""

from __future__ import annotations
import json
import re
from typing import Optional, List, Dict
from langchain_community.vectorstores import FAISS

from modules.rag_engine import get_llm, RAGError
from modules.vector_store import similarity_search, VectorStoreError


def _extract_json(raw_text: str):
    """Strip markdown code fences and parse the model's JSON response."""
    cleaned = re.sub(r"```(json)?", "", raw_text).strip()
    return json.loads(cleaned)


def generate_quiz(
    store: Optional[FAISS],
    question_types: List[str],
    num_questions: int = 5,
    topic_hint: str = "",
    difficulty: str = "Medium",
) -> List[Dict]:
    """
    Generate a list of quiz question dicts, each shaped like:
    {
      "type": "MCQ" | "True/False" | "Short Answer",
      "question": str,
      "options": List[str] | None,
      "correct_answer": str,
      "explanation": str
    }
    """
    if store is None:
        raise RAGError("Please upload study material first before generating a quiz.")

    query = topic_hint.strip() if topic_hint.strip() else "key concepts and important facts"

    try:
        chunks = similarity_search(store, query, k=10)
    except VectorStoreError as exc:
        raise RAGError(str(exc)) from exc

    if not chunks:
        raise RAGError("This is not available in your uploaded notes.")

    context = "\n\n---\n\n".join(doc.page_content for doc in chunks)
    types_str = ", ".join(question_types)

    prompt = f"""You are a quiz generator for a university student. Using ONLY the
notes provided below, create exactly {num_questions} quiz questions at {difficulty}
difficulty, using a mix of these question types: {types_str}.

Respond ONLY with valid JSON — a list of objects, no preamble, no markdown fences.
Each object must follow this exact schema:
{{
  "type": "MCQ" | "True/False" | "Short Answer",
  "question": "the question text",
  "options": ["A", "B", "C", "D"]  (ONLY for MCQ, otherwise null),
  "correct_answer": "the correct answer text",
  "explanation": "a short explanation of why this is correct, referencing the notes"
}}

Notes:
{context}

JSON:"""

    try:
        llm = get_llm(temperature=0.5)
        response = llm.invoke(prompt)
        quiz_data = _extract_json(response.content)
        if not isinstance(quiz_data, list) or not quiz_data:
            raise RAGError("The AI did not return any usable quiz questions. Try again.")
        return quiz_data
    except RAGError:
        raise
    except json.JSONDecodeError as exc:
        raise RAGError(f"The AI's quiz response couldn't be parsed. Please try again. ({exc})") from exc
    except Exception as exc:
        raise RAGError(f"Failed to generate quiz: {exc}") from exc
