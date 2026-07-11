"""
Why this file exists:
    The assignment requires an evaluation framework for chatbot responses.

Responsibility:
    - Score context relevance.
    - Score faithfulness.
    - Score answer correctness using available context as a reference.
    - Score groundedness.

How it connects to the project:
    The LangGraph Evaluation node calls this evaluator. Streamlit displays the
    returned scores after every chat response.
"""

from typing import Dict

from app.utils.text import word_set


def _overlap_score(a: str, b: str) -> float:
    """Return a simple 0-1 word overlap score."""
    words_a = word_set(a)
    words_b = word_set(b)
    if not words_a or not words_b:
        return 0.0
    return round(len(words_a.intersection(words_b)) / max(1, len(words_a)), 2)


class Evaluator:
    """Lightweight evaluation suitable for a free beginner project."""

    def evaluate(self, question: str, answer: str, context: str) -> Dict[str, float]:
        """Evaluate answer quality using transparent heuristic metrics."""
        context_relevance = _overlap_score(question, context)
        faithfulness = _overlap_score(answer, context)
        answer_correctness = round((_overlap_score(question, answer) + faithfulness) / 2, 2)
        groundedness = faithfulness

        return {
            "context_relevance": context_relevance,
            "faithfulness": faithfulness,
            "answer_correctness": answer_correctness,
            "groundedness": groundedness,
        }
