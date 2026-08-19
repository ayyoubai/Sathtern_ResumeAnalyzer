from typing import Optional

from pydantic import BaseModel, Field


# ============================================================
# PERSONAL INFORMATION
# ============================================================

class PersonalInfo(BaseModel):

    name: Optional[str] = None

    email: Optional[str] = None

    phone: Optional[str] = None

    location: Optional[str] = None


# ============================================================
# EXPERIENCE
# ============================================================

class Experience(BaseModel):

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

    text: str | None = None

    target_role: Optional[str] = None


# ============================================================
# SKILL MATCH
# ============================================================

class SkillMatch(BaseModel):

    skill: str

    status: str


# ============================================================
# RESUME ANALYSIS
# ============================================================

class ResumeAnalysis(BaseModel):

    # Poste sélectionné par l'utilisateur
    target_role: str

    # Compatibilité du CV avec le poste
    match_score: int

    # Points forts
    strengths: list[str] = Field(
        default_factory=list
    )

    # Compétences importantes absentes
    missing_skills: list[str] = Field(
        default_factory=list
    )

    # Correspondance des compétences
    skills_match: list[SkillMatch] = Field(
        default_factory=list
    )

    # Recommandations
    recommendations: list[str] = Field(
        default_factory=list
    )

    # Améliorations du CV
    cv_improvements: list[str] = Field(
        default_factory=list
    )