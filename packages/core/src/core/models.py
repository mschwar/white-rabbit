from typing import Literal

from pydantic import BaseModel, Field


class Lead(BaseModel):
    id: str | None = Field(default=None, description="Database lead ID (set after persistence)")
    name: str = Field(description="First and last name of the contact")
    title: str = Field(description="Job title")
    organization: str = Field(description="Organization, district, agency, or company name")
    email: str = Field(description="Professional email address, or blank if unavailable")
    email_status: Literal["Found", "Deduced", "Missing"] = Field(
        description="Email evidence status: Found, Deduced, or Missing"
    )
    source_url: str = Field(description="Best source URL supporting the contact, title, or email")
    confidence: float = Field(
        ge=0,
        le=1,
        description="DEPRECATED: Confidence score from 0.0 to 1.0 based on source strength. Use scores instead.",
    )
    why_target: str = Field(description="1 sentence on why this role is good for VoIP sales")
    icebreaker: str = Field(
        description="A specific 1-sentence cold email opener referencing their job title, their organization type, and one concrete reason a VoIP upgrade matters to them"
    )
    
    # New Sprint 1 fields
    fit_score: float = Field(ge=0, le=1, description="Match between person/org and target ICP")
    evidence_score: float = Field(ge=0, le=1, description="Strength and freshness of supporting sources")
    contact_score: float = Field(ge=0, le=1, description="Usability of email/phone/title information")
    gate_passed: bool = Field(description="True if all three scores cleared their thresholds")
    explanation: str = Field(description="Human-readable rationale for ranking")


class LeadList(BaseModel):
    leads: list[Lead] = Field(description="List of extracted leads")
