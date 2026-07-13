from collections import defaultdict

from app.utils.csv_loader import load_icd_codes


class ICD10Hierarchy:
    """Category-level ICD-10-CM hierarchy derived from the code strings themselves.

    Every ICD-10-CM code's first three characters are its category (e.g. I25.2 -> I25),
    so codes sharing a category are clinically related even when RAG only surfaces one
    of them. This does not include Excludes1/Excludes2 or "code also" relationships -
    those require CMS's Tabular List, which isn't part of the current dataset.
    """

    def __init__(self, dataframe):
        self.description_by_code = dict(zip(dataframe["code"], dataframe["description"]))
        self.codes_by_category = defaultdict(list)

        for code in dataframe["code"]:
            self.codes_by_category[self._category(code)].append(code)

    @staticmethod
    def _category(code: str) -> str:
        return code.split(".")[0]

    def get_related_codes(self, code: str, limit: int = 5):
        category = self._category(code)
        siblings = [c for c in self.codes_by_category.get(category, []) if c != code]

        return [
            {"code": sibling, "description": self.description_by_code[sibling]}
            for sibling in siblings[:limit]
        ]


_hierarchy = None


def get_icd_hierarchy() -> ICD10Hierarchy:
    global _hierarchy

    if _hierarchy is None:
        _hierarchy = ICD10Hierarchy(load_icd_codes())

    return _hierarchy
