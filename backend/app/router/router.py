from typing import Any

from backend.app.router.model_registry import (
    get_model_for_tier,
)


def select_tier(
    analysis: dict[str, Any],
    document_size_bytes: int | None = None,
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

    # Demo routing policy: prompts without a document use Tier 3;
    # documents use Tier 2 up to 2 MiB and Tier 1 above that limit.
    if document_size_bytes is not None:
        if document_size_bytes > 2 * 1024 * 1024:
            tier = "LOW"
        else:
            tier = "MEDIUM"
    else:
        tier = "HIGH"

    model = get_model_for_tier(tier)

    reason = (
        f"Task: {analysis['task_type']}. "
        f"Complexity: {complexity}/10. "
        f"Reasoning: {reasoning}. "
        f"Estimated context: {context_tokens} tokens. "
        (
            f"No document attached; using Tier 3 ({tier})."
            if document_size_bytes is None
            else f"Document size is {document_size_bytes} bytes; "
            f"using the {'Tier 1' if tier == 'LOW' else 'Tier 2'} ({tier}) demo rule."
        )
    )

    return {
        "tier": tier,
        "model": model,
        "reason": reason,
    }
