from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional # Added Optional

class QueryRequest(BaseModel):
    """
    Defines the structure for an incoming user query.

    """
    question: str = Field(..., description="The user's current question.")
    chat_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="A list of previous chat messages to maintain conversation context."
    )
    filter_on_metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata to filter documents for retrieval.")

class PolicyResponse(BaseModel):
    """
    Defines the structured JSON output for the API response.

    """
    summary: str = Field(description="A concise summary of the answer based on the policies.")
    bullets: List[str] = Field(
        default_factory=list,
        description="Key points or relevant excerpts from the policy documents as a list of strings."
    )

class ErrorResponse(BaseModel):
    """
    Standard error response structure for API errors.
    """
    error: str = Field(description="A description of the error that occurred.")
    details: Any = Field(None, description="Optional additional details about the error.")
