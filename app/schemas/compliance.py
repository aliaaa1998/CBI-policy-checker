from pydantic import BaseModel, Field
from app.schemas.common import Citation


class Violation(BaseModel):
    issue: str
    severity: str
    explanation: str
    citation: Citation


class RelevantClause(BaseModel):
    clause_text: str
    citation: Citation


class ComplianceRequest(BaseModel):
    scenario: str = Field(min_length=5)
    response_language: str = "ar"
    top_k: int | None = None


class ComplianceResponse(BaseModel):
    verdict: str
    summary: str
    violations: list[Violation]
    relevant_clauses: list[RelevantClause]
    required_actions: list[str]
    confidence: str
    needs_human_review: bool
    request_id: str
