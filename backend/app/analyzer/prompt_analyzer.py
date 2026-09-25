import json
import re
from typing import Any

from openai import OpenAI

from backend.app.analyzer.scoring import (
    fallback_analysis,
    finalize_analysis,
)
from backend.app.config import (
    ANALYZER_MODEL,
    OPENAI_API_KEY,
    MAX_CONTENT_CHARS,
)


class PromptAnalyzer:
    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=OPENAI_API_KEY
        )

    def _extract_json(
        self,
        text: str,
    ) -> dict[str, Any]:

        cleaned = text.strip()

        cleaned = re.sub(
            r"^```json\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned,
        )

        match = re.search(
            r"\{.*\}",
            cleaned,
            flags=re.DOTALL,
        )

        if not match:
            raise ValueError(
                "Analyzer did not return JSON."
            )

        return json.loads(match.group(0))

    def analyze(self, text: str) -> dict[str, Any]:
        """
        Ask a lightweight model for structured classification.
        The model analyzes the request; our backend owns the
        actual tier-selection policy.
        """

        analysis_input = text[:MAX_CONTENT_CHARS]

        instructions = """
You are the analysis component of PromptGuard-AI.

Your job is NOT to answer the user's request.

Your job is to classify the request for an LLM routing gateway.

Return ONLY valid JSON:

{
  "task_type": "short descriptive task category",
  "complexity": 0,
  "reasoning_required": "low|medium|high",
  "reasoning_rationale": "one short sentence"
}

Rules:

- complexity must be a number from 0 to 10
- low = simple factual, formatting, basic lookup-like questions
- medium = explanation, summarization, comparison, moderate coding
- high = complex reasoning, multi-step analysis, large document analysis,
  advanced coding, conflicting information, or difficult professional work
- Do not answer the user.
"""

        try:
            response = self.client.responses.create(
                model=ANALYZER_MODEL,
                instructions=instructions,
                input=analysis_input,
                max_output_tokens=350,
            )

            raw_text = response.output_text

            raw_analysis = self._extract_json(
                raw_text
            )

            return finalize_analysis(
                raw_analysis,
                text,
            )

        except Exception:
            return fallback_analysis(text)