from typing import Optional

from pydantic import BaseModel, Field


# ============================================================
# PERSONAL INFORMATION
# ============================================================

class PersonalInfo(BaseModel):
    """Candidate personal contact information."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None


# ============================================================
# EXPERIENCE
# ============================================================

class Experience(BaseModel):
    """Professional work experience entry."""

    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


# ============================================================
# EDUCATION
# ============================================================

class Education(BaseModel):
    """Academic education and training entry."""

    degree: Optional[str] = None
    institution: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    description: Optional[str] = None


# ============================================================
# PROJECT
# ============================================================

class Project(BaseModel):
    """Academic or personal project entry."""

    title: Optional[str] = None
    institution: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


# ============================================================
# RESUME DATA
# ============================================================

class ResumeData(BaseModel):
    """Structured resume data extracted from a PDF."""

    personal_info: PersonalInfo = Field(
        default_factory=PersonalInfo
    )

    skills: list[str] = Field(
        default_factory=list
    )

    experiences: list[Experience] = Field(
        default_factory=list
    )

    education: list[Education] = Field(
        default_factory=list
    )

    projects: list[Project] = Field(
        default_factory=list
    )

    certificates: list[str] = Field(
        default_factory=list
    )


# ============================================================
# ANALYZE REQUEST
# ============================================================

class AnalyzeRequest(BaseModel):
    """Request payload for resume analysis against a target role."""

    text: str | None = None
    target_role: Optional[str] = None


# ============================================================
# SKILL MATCH
# ============================================================

class SkillMatch(BaseModel):
    """Skill match status: strong or missing."""

    skill: str
    status: str


# ============================================================
# RESUME ANALYSIS
# ============================================================

class ResumeAnalysis(BaseModel):
    """Complete AI-powered resume analysis result."""

    # Target job position selected by the user
    target_role: str

    # Compatibility score between resume and job position (0-100)
    match_score: int

    # Candidate main strengths
    strengths: list[str] = Field(
        default_factory=list
    )

    # Important skills missing from the resume
    missing_skills: list[str] = Field(
        default_factory=list
    )

    # Individual skill match against the target position
    skills_match: list[SkillMatch] = Field(
        default_factory=list
    )

    # Personalized recommendations for the candidate
    recommendations: list[str] = Field(
        default_factory=list
    )

    # Suggested CV improvements
    cv_improvements: list[str] = Field(
        default_factory=list
    )
