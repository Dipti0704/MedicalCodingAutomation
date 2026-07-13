from fastapi import FastAPI
from app.models.medical_input import MedicalTextInput
from app.agents.analyzer_agent import AnalyzerAgent
from app.agents.validator_agent import ValidatorAgent
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

@app.get("/")
def root():
    return {"message": "Medical Coding API is running"}

@app.post("/analyze-text")
def analyze_text(input: MedicalTextInput):
    analysis_result = analyzer.analyze(input.text)
    warnings = validator.validate(analysis_result)

    return {
        "analysis": analysis_result,
        "warnings": warnings
    }
