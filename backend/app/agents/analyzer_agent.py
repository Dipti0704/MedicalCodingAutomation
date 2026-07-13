from app.rag.index_cache import get_stores

class AnalyzerAgent:
    def __init__(self, threshold=75):
        self.threshold = threshold
        self.icd_store, self.cpt_store = get_stores()

    def analyze(self, text: str):
        text_lower = text.lower()

        icd_results = self.icd_store.search(text)
        icd_filtered = [
            c for c in icd_results
            if c["confidence"] >= self.threshold
        ]

        # Procedure trigger keywords
        procedure_triggers = [
            "x-ray", "xray", "ecg", "ekg", "scan",
            "ct", "mri", "ultrasound", "blood test",
            "biopsy"
        ]

        has_procedure_mention = any(
            trigger in text_lower for trigger in procedure_triggers
        )

        cpt_filtered = []
        if has_procedure_mention:
            cpt_results = self.cpt_store.search(text)
            cpt_filtered = [
                c for c in cpt_results
                if c["confidence"] >= self.threshold
            ]

        return {
            "icd_codes": icd_filtered,
            "cpt_codes": cpt_filtered
        }
