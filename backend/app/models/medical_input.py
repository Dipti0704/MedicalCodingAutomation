from pydantic import BaseModel

class MedicalTextInput(BaseModel):
    text: str
