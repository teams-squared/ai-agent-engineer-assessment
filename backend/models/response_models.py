from pydantic import BaseModel, Field
from typing import List

class PolicyAnswer(BaseModel):
    summary: str = Field(description="A one-sentence summary of the answer")
    bullets: List[str] = Field(description="List of bullet points with key details")