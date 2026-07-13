from typing import Literal

from pydantic import BaseModel


class ReviewDecision(BaseModel):
    status: Literal["approved", "rejected"]
