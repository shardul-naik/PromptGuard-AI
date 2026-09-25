from typing import Final

from backend.app.config import (
    LOW_MODEL,
    MEDIUM_MODEL,
    HIGH_MODEL,
)


MODEL_REGISTRY: Final[dict[str, str]] = {
    "LOW": LOW_MODEL,
    "MEDIUM": MEDIUM_MODEL,
    "HIGH": HIGH_MODEL,
}


def get_model_for_tier(tier: str) -> str:
    try:
        return MODEL_REGISTRY[tier]
    except KeyError as exc:
        raise ValueError(
            f"Unknown routing tier: {tier}"
        ) from exc