import re


PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?prior\s+instructions",
    r"disregard\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?prior\s+instructions",
    r"forget\s+(everything|all)\s+(you|that)\s+(were|have been)\s+told",
    r"system\s+message",
    r"reveal\s+your\s+system\s+prompt",
    r"show\s+me\s+your\s+system\s+prompt",
    r"developer\s+message",
    r"bypass\s+(your\s+)?safety",
    r"disable\s+(your\s+)?safety",
    r"jailbreak",
    r"do\s+anything\s+now",
]


def detect_prompt_injection(text: str) -> list[str]:
    """
    Detect common prompt-injection/jailbreak patterns.

    This is intentionally lightweight. It complements the
    OpenAI moderation layer rather than attempting to be a
    complete security engine.
    """

    findings: list[str] = []

    lowered = text.lower()

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            findings.append(pattern)

    return findings