class ValidatorAgent:
    def validate(self, analysis_result):
        warnings = []

        icd_codes = analysis_result.get("icd_codes", [])
        cpt_codes = analysis_result.get("cpt_codes", [])

        # Rule 1: No diagnosis found
        if not icd_codes:
            warnings.append("No ICD-10 diagnosis codes detected. Clinical note may be incomplete.")

        # Rule 2: No procedure found
        if not cpt_codes:
            warnings.append("No CPT procedure codes detected. Procedures may be missing.")

        # Rule 3: Low confidence codes
        for code in icd_codes + cpt_codes:
            if code["confidence"] < 30:
                warnings.append(
                    f"Low confidence for code {code['code']} ({code['description']}). Review recommended."
                )

        return warnings
