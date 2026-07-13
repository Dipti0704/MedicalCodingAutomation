import logging
import os

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

logger = logging.getLogger(__name__)

MODEL = "claude-haiku-4-5-20251001"


class LLMReasoningAgent:
    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=api_key) if (Anthropic and api_key) else None

    @property
    def available(self):
        return self.client is not None

    def explain(self, clinical_text: str, code_type: str, code: str, description: str):
        prompt = (
            f"Clinical note:\n{clinical_text}\n\n"
            f"Candidate {code_type.upper()} code: {code} - {description}\n\n"
            "In 2-3 sentences, explain whether this code is clinically justified by the note, "
            "quoting the specific phrase that supports it. If it is not well supported, say so plainly."
        )

        response = self.client.messages.create(
            model=MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text.strip()
