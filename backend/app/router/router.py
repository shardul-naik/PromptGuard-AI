from typing import Any

from backend.app.config import (
    HIGH_THRESHOLD,
    LOW_THRESHOLD,
)
from backend.app.router.model_registry import (
    get_model_for_tier,
)


def select_tier(
    analysis: dict[str, Any]
) -> dict[str, Any]:

    complexity = float(
        analysis["complexity"]
    )

    reasoning = str(
        analysis["reasoning_required"]
    ).lower()

    context_tokens = int(
        analysis["context"]["estimated_tokens"]
    )

    # HIGH
    if (
        complexity >= HIGH_THRESHOLD
        or reasoning == "high"
        or context_tokens >= 25000
    ):
        tier = "HIGH"

    # MEDIUM
    elif (
        complexity >= LOW_THRESHOLD
        or reasoning == "medium"
        or context_tokens >= 5000
    ):
        tier = "MEDIUM"

    # LOW
    else:
        tier = "LOW"

    model = get_model_for_tier(tier)

    reason = (
        f"Task: {analysis['task_type']}. "
        f"Complexity: {complexity}/10. "
        f"Reasoning: {reasoning}. "
        f"Estimated context: {context_tokens} tokens. "
        f"Required capability maps to the {tier} tier."
    )

    return {
        "tier": tier,
        "model": model,
        "reason": reason,
    }