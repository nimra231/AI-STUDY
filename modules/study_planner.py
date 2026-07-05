"""
study_planner.py
-----------------
Builds a day-by-day study schedule between today and the user's exam
date, allocating the uploaded topics across the available daily study
hours. Uses the LLM to intelligently sequence and balance topics, but
falls back to the raw document list if no vector store is available.
"""

from __future__ import annotations
from datetime import date
from typing import Optional, List, Dict
import json
import re

from langchain_community.vectorstores import FAISS

from modules.rag_engine import get_llm, RAGError


def _extract_json(raw_text: str):
    cleaned = re.sub(r"```(json)?", "", raw_text).strip()
    return json.loads(cleaned)


def generate_study_plan(
    source_names: List[str],
    exam_date: date,
    daily_hours: float,
    notes_preview: Optional[str] = None,
) -> List[Dict]:
    """
    Returns a list of daily plan entries:
    [{"day": "2026-07-06", "focus_topics": [...], "tasks": [...], "hours": 2}]
    """
    days_remaining = (exam_date - date.today()).days
    if days_remaining <= 0:
        raise RAGError("The exam date must be in the future.")

    if not source_names:
        raise RAGError("Please upload at least one document so a plan can be built around it.")

    context_note = f"\nSample of the material:\n{notes_preview[:3000]}" if notes_preview else ""

    prompt = f"""You are an academic study planner. A student has {days_remaining} day(s)
until their exam and can study {daily_hours} hour(s) per day. Their uploaded study
materials are: {", ".join(source_names)}.
{context_note}

Create a realistic, well-paced day-by-day study plan from today until the exam date,
covering all materials, including at least one light revision day near the end and
one final full-revision day right before the exam.

Respond ONLY with valid JSON, no markdown fences, as a list of objects:
[
  {{
    "day": "Day 1",
    "focus_topics": ["topic A", "topic B"],
    "tasks": ["Read chapter 1", "Make flashcards for key terms"],
    "hours": {daily_hours}
  }}
]

JSON:"""

    try:
        llm = get_llm(temperature=0.4)
        response = llm.invoke(prompt)
        plan = _extract_json(response.content)
        if not isinstance(plan, list) or not plan:
            raise RAGError("The AI did not return a usable study plan. Try again.")
        return plan
    except RAGError:
        raise
    except json.JSONDecodeError as exc:
        raise RAGError(f"The AI's plan response couldn't be parsed. Please try again. ({exc})") from exc
    except Exception as exc:
        raise RAGError(f"Failed to generate study plan: {exc}") from exc
