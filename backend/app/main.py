import logging

from fastapi import FastAPI, UploadFile, File, HTTPException
from app.models.medical_input import MedicalTextInput
from app.models.review import ReviewDecision
from app.agents.analyzer_agent import AnalyzerAgent
from app.agents.validator_agent import ValidatorAgent
from app.agents.explanation_agent import ExplanationAgent
from app.agents.llm_agent import LLMReasoningAgent
from app.utils.file_extractor import extract_text, TesseractNotAvailable
from app.graph.icd_hierarchy import get_icd_hierarchy
from fastapi.middleware.cors import CORSMiddleware
from app import db

logger = logging.getLogger(__name__)

app = FastAPI(title="Medical Coding Automation API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = AnalyzerAgent()
validator = ValidatorAgent()
explainer = ExplanationAgent()
llm_agent = LLMReasoningAgent()
icd_hierarchy = get_icd_hierarchy()

db.init_db()

@app.get("/")
def root():
    return {"message": "Medical Coding API is running"}

def build_explanation(clinical_text: str, code_type: str, code_item: dict) -> str:
    if llm_agent.available:
        try:
            return llm_agent.explain(clinical_text, code_type, code_item["code"], code_item["description"])
        except Exception:
            logger.warning("LLM explanation failed, falling back to templated explanation", exc_info=True)

    return explainer.explain(clinical_text, [code_item])[0]["explanation"]

@app.post("/analyze-text")
def analyze_text(input: MedicalTextInput):
    analysis_result = analyzer.analyze(input.text)
    warnings = validator.validate(analysis_result)

    session_id = db.create_session(input.text)

    for code_type, key in (("icd", "icd_codes"), ("cpt", "cpt_codes")):
        explained_codes = []

        for code_item in analysis_result[key]:
            code_item = {**code_item, "explanation": build_explanation(input.text, code_type, code_item)}
            review_id = db.add_code_review(session_id, code_type, code_item)

            related_codes = (
                icd_hierarchy.get_related_codes(code_item["code"]) if code_type == "icd" else []
            )

            explained_codes.append(
                {**code_item, "review_id": review_id, "status": "pending", "related_codes": related_codes}
            )

        analysis_result[key] = explained_codes

    return {
        "session_id": session_id,
        "analysis": analysis_result,
        "warnings": warnings
    }

@app.post("/reviews/{review_id}/decision")
def decide_review(review_id: int, decision: ReviewDecision):
    updated = db.update_review_status(review_id, decision.status)

    if updated is None:
        raise HTTPException(status_code=404, detail="Review not found")

    return updated

@app.get("/sessions/{session_id}")
def get_session(session_id: int):
    session = db.get_session(session_id)

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return session

@app.post("/extract-text")
async def extract_text_endpoint(file: UploadFile = File(...)):
    file_bytes = await file.read()

    try:
        return extract_text(file.filename, file_bytes)
    except TesseractNotAvailable as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
