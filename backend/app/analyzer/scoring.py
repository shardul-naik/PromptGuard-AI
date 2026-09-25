import math
from typing import Any


def estimate_context(text: str) -> dict[str, Any]:
    character_count = len(text)
    word_count = len(text.split())

    # Approximation only.
    # Exact token counts differ between tokenizers/models.
    estimated_tokens = max(
        1,
        math.ceil(character_count / 4),
    )

    return {
        "character_count": character_count,
        "word_count": word_count,
        "estimated_tokens": estimated_tokens,
    }


def heuristic_complexity(text: str) -> float:
    lowered = text.lower()

    score = 2.0

    high_complexity_terms = [
        "analyze",
        "analyse",
        "compare",
        "evaluate",
        "derive",
        "design",
        "debug",
        "architect",
        "contradiction",
        "reason",
        "justify",
        "trade-off",
        "tradeoff",
        "financial analysis",
        "legal analysis",
        "research",
        "deep analysis",
        "document analysis",
    ]

    medium_complexity_terms = [
        "explain",
        "summarize",
        "summary",
        "difference",
        "describe",
        "how does",
        "why does",
        "examples",
    ]

    simple_terms = [
        "what is",
        "who is",
        "when is",
        "where is",
        "capital of",
        "today's date",
        "current date",
        "yes or no",
        "define",
    ]

    high_hits = sum(
        term in lowered
        for term in high_complexity_terms
    )

    medium_hits = sum(
        term in lowered
        for term in medium_complexity_terms
    )

    simple_hits = sum(
        term in lowered
        for term in simple_terms
    )

    score += min(high_hits * 1.4, 4.5)
    score += min(medium_hits * 0.8, 2.5)
    score -= min(simple_hits * 0.8, 1.5)

    return max(0.0, min(10.0, score))


def fallback_analysis(text: str) -> dict[str, Any]:
    score = heuristic_complexity(text)
    context = estimate_context(text)

    if score >= 7:
        reasoning = "high"
    elif score >= 4:
        reasoning = "medium"
    else:
        reasoning = "low"

    if "document" in text.lower() or context["estimated_tokens"] > 5000:
        task_type = "document_analysis"
    elif any(
        word in text.lower()
        for word in ["code", "python", "javascript", "sql", "debug"]
    ):
        task_type = "coding"
    elif any(
        word in text.lower()
        for word in ["summarize", "summary"]
    ):
        task_type = "summarization"
    elif any(
        word in text.lower()
        for word in ["compare", "difference"]
    ):
        task_type = "comparison"
    else:
        task_type = "general_question"

    return {
        "task_type": task_type,
        "complexity": round(score, 2),
        "reasoning_required": reasoning,
        "reasoning_rationale": (
            "Heuristic fallback analysis was used."
        ),
        "context": context,
    }


def finalize_analysis(
    raw_analysis: dict[str, Any],
    text: str,
) -> dict[str, Any]:

    context = estimate_context(text)

    try:
        llm_score = float(
            raw_analysis.get("complexity", 2.0)
        )
    except (TypeError, ValueError):
        llm_score = 2.0

    heuristic_score = heuristic_complexity(text)

    tokens = context["estimated_tokens"]

    if tokens >= 25000:
        context_score = 8.0
    elif tokens >= 12000:
        context_score = 6.5
    elif tokens >= 5000:
        context_score = 5.0
    else:
        context_score = 2.0

    final_score = (
        llm_score * 0.70
        + heuristic_score * 0.20
        + context_score * 0.10
    )

    final_score = max(
        0.0,
        min(10.0, final_score),
    )

    reasoning = str(
        raw_analysis.get(
            "reasoning_required",
            "low",
        )
    ).lower()

    if reasoning not in {"low", "medium", "high"}:
        reasoning = "low"

    return {
        "task_type": str(
            raw_analysis.get(
                "task_type",
                "general_question",
            )
        ),
        "complexity": round(final_score, 2),
        "reasoning_required": reasoning,
        "reasoning_rationale": str(
            raw_analysis.get(
                "reasoning_rationale",
                "Prompt characteristics were evaluated.",
            )
        ),
        "context": context,
    }