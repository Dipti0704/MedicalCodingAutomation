from app.rag.vector_store import VectorStore
from app.utils.csv_loader import load_icd_codes, load_cpt_codes

_icd_store = None
_cpt_store = None

def get_stores():
    global _icd_store, _cpt_store

    if _icd_store is None or _cpt_store is None:
        icd_df = load_icd_codes()
        cpt_df = load_cpt_codes()

        _icd_store = VectorStore(icd_df)
        _cpt_store = VectorStore(cpt_df)

    return _icd_store, _cpt_store
