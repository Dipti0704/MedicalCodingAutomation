class ExplanationAgent:
    def explain(self, clinical_text, codes):
        explained = []

        for code in codes:
            explanation = (
                f"The clinical note contains information that semantically matches "
                f"the medical concept '{code['description']}', which is represented "
                f"by the code {code['code']}. The confidence score reflects the "
                f"similarity between the note and the standardized description."
            )

            explained.append({
                **code,
                "explanation": explanation
            })

        return explained
