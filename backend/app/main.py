from fastapi import FastAPI, UploadFile, File, HTTPException
from app.models.medical_input import MedicalTextInput
from app.agents.analyzer_agent import AnalyzerAgent
from app.agents.validator_agent import ValidatorAgent
from app.agents.explanation_agent import ExplanationAgent
from app.utils.file_extractor import extract_text, TesseractNotAvailable
from fastapi.middleware.cors import CORSMiddleware


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

@app.get("/")
def root():
    return {"message": "Medical Coding API is running"}

@app.post("/analyze-text")
def analyze_text(input: MedicalTextInput):
    analysis_result = analyzer.analyze(input.text)
    warnings = validator.validate(analysis_result)

    analysis_result["icd_codes"] = explainer.explain(input.text, analysis_result["icd_codes"])
    analysis_result["cpt_codes"] = explainer.explain(input.text, analysis_result["cpt_codes"])

    return {
        "analysis": analysis_result,
        "warnings": warnings
    }

@app.post("/extract-text")
async def extract_text_endpoint(file: UploadFile = File(...)):
    file_bytes = await file.read()

    try:
        return extract_text(file.filename, file_bytes)
    except TesseractNotAvailable as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
