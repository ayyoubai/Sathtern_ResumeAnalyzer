import json
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from groq import Groq

from app.schemas import (
    ResumeData,
    PersonalInfo,
    ResumeAnalysis,
)


# ============================================================
# ENVIRONMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError(
        f"GROQ_API_KEY not found. "
        f"Please check the file: {ENV_FILE}"
    )

client = Groq(api_key=api_key)

MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)


# ============================================================
# LIMITS
# ============================================================

# Avoid cutting CVs too short.
# 12000 characters remains reasonable for analysis.
MAX_INPUT_CHARS = 12000

MAX_SKILLS = 30
MAX_EXPERIENCES = 10
MAX_EDUCATION = 10
MAX_PROJECTS = 10
MAX_CERTIFICATES = 10

MAX_STRENGTHS = 6
MAX_MISSING_SKILLS = 8
MAX_SKILLS_MATCH = 15
MAX_RECOMMENDATIONS = 6
MAX_CV_IMPROVEMENTS = 6


# ============================================================
# REFERENCE SKILLS
# ============================================================

REFERENCE_SKILLS = [
    # --------------------------------------------------------
    # FRONTEND
    # --------------------------------------------------------

    "HTML",
    "CSS",
    "JavaScript",
    "TypeScript",
    "Angular",
    "React",
    "Vue.js",
    "Next.js",

    # --------------------------------------------------------
    # BACKEND
    # --------------------------------------------------------

    "Node.js",
    "Express",
    "Java",
    "Spring Boot",
    "PHP",
    "Laravel",
    "Python",
    "ASP.NET",
    ".NET",
    "ASP.NET Core",
    "C#",
    "C++",
    "NestJS",
    "FastAPI",

    # --------------------------------------------------------
    # API / ARCHITECTURE
    # --------------------------------------------------------

    "REST API",
    "REST",
    "API Development",
    "Microservices",
    "API Gateway",
    "Swagger",
    "OpenAPI",

    # --------------------------------------------------------
    # DATABASES
    # --------------------------------------------------------

    "SQL",
    "MySQL",
    "PostgreSQL",
    "SQL Server",
    "MongoDB",
    "Redis",
    "Prisma",

    # --------------------------------------------------------
    # DEVOPS
    # --------------------------------------------------------

    "Docker",
    "Kubernetes",
    "Git",
    "GitHub",
    "GitLab",
    "CI/CD",
    "GitHub Actions",
    "GitLab CI",

    # --------------------------------------------------------
    # CLOUD
    # --------------------------------------------------------

    "AWS",
    "Azure",
    "GCP",

    # --------------------------------------------------------
    # TESTING
    # --------------------------------------------------------

    "JUnit",
    "Jest",
    "Selenium",
    "Unit Testing",

    # --------------------------------------------------------
    # DATA
    # --------------------------------------------------------

    "Pandas",
    "NumPy",
    "Matplotlib",
    "Seaborn",
    "Tableau",
    "Power BI",
    "Excel",
    "ETL",

    # --------------------------------------------------------
    # DATA SCIENCE / MACHINE LEARNING
    # --------------------------------------------------------

    "Machine Learning",
    "Deep Learning",
    "Scikit-learn",
    "TensorFlow",
    "PyTorch",
    "Statistics",
    "Statistical Analysis",
    "Data Visualization",
    "Big Data",
    "Spark",
    "Hadoop",
    "R",

    # --------------------------------------------------------
    # MESSAGING / STORAGE
    # --------------------------------------------------------

    "Kafka",
    "MinIO",

    # --------------------------------------------------------
    # SECURITY
    # --------------------------------------------------------

    "OAuth",
    "JWT",
    "OWASP",
    "Networking",
    "Linux",

    # --------------------------------------------------------
    # METHODOLOGIES
    # --------------------------------------------------------

    "Agile",
    "Scrum",
]


# ============================================================
# ROLE SKILL PROFILES
# ============================================================

ROLE_SKILLS = {

    "Full Stack Developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "TypeScript",
        "Angular",
        "React",
        "Node.js",
        "Java",
        "Spring Boot",
        "Python",
        "PHP",
        "Laravel",
        ".NET",
        "ASP.NET Core",
        "REST API",
        "Microservices",
        "API Gateway",
        "SQL",
        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "Docker",
        "Git",
        "GitHub",
    ],

    "Frontend Developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "TypeScript",
        "Angular",
        "React",
        "Vue.js",
        "Next.js",
        "REST API",
        "Git",
        "GitHub",
    ],

    "Backend Developer": [
        "Java",
        "Spring Boot",
        "Python",
        "FastAPI",
        "PHP",
        "Laravel",
        "Node.js",
        "NestJS",
        ".NET",
        "ASP.NET Core",
        "REST API",
        "Microservices",
        "API Gateway",
        "SQL",
        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "Docker",
        "Git",
    ],

    "Software Engineer": [
        "Java",
        "Python",
        "C++",
        "C#",
        ".NET",
        "ASP.NET Core",
        "JavaScript",
        "TypeScript",
        "REST API",
        "Microservices",
        "SQL",
        "Git",
        "GitHub",
        "Docker",
        "Unit Testing",
    ],

    "DevOps Engineer": [
        "Linux",
        "Docker",
        "Kubernetes",
        "CI/CD",
        "GitHub Actions",
        "GitLab CI",
        "AWS",
        "Azure",
        "GCP",
        "Git",
        "Prometheus",
        "Grafana",
    ],

    "Data Analyst": [
        "Python",
        "SQL",
        "Pandas",
        "NumPy",
        "Excel",
        "Statistics",
        "Data Visualization",
        "Matplotlib",
        "Seaborn",
        "Power BI",
        "Tableau",
    ],

    "Data Scientist": [
        "Python",
        "SQL",
        "Pandas",
        "NumPy",
        "Statistics",
        "Machine Learning",
        "Scikit-learn",
        "Data Visualization",
        "Matplotlib",
        "Seaborn",
    ],

    "AI Engineer": [
        "Python",
        "Machine Learning",
        "Deep Learning",
        "Scikit-learn",
        "TensorFlow",
        "PyTorch",
        "NumPy",
        "Pandas",
        "FastAPI",
        "Docker",
    ],

    "Machine Learning Engineer": [
        "Python",
        "Machine Learning",
        "Deep Learning",
        "Scikit-learn",
        "TensorFlow",
        "PyTorch",
        "Pandas",
        "NumPy",
        "Docker",
        "FastAPI",
    ],

    "Cybersecurity Engineer": [
        "Python",
        "Linux",
        "Networking",
        "OWASP",
        "OAuth",
        "JWT",
        "Docker",
        "Git",
    ],
}


# ============================================================
# SKILL ALIASES
# ============================================================

# Prevents false "missing" skills by normalizing variants.
#
# Example:
#   SpringBoot in the CV
#   Spring Boot in ROLE_SKILLS
#
# => same skill.
#

SKILL_ALIASES = {

    "springboot": "spring boot",
    "spring boot": "spring boot",

    "aspnet": "asp.net",
    "asp net": "asp.net",

    "aspnet core": "asp.net core",
    "asp net core": "asp.net core",

    "dotnet": ".net",
    "dot net": ".net",

    "nodejs": "node.js",
    "node js": "node.js",

    "nextjs": "next.js",
    "next js": "next.js",

    "nestjs": "nestjs",
    "nest js": "nestjs",

    "vuejs": "vue.js",
    "vue js": "vue.js",

    "postgres": "postgresql",

    "mongo": "mongodb",

    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",

    "machine-learning": "machine learning",
    "machinelearning": "machine learning",

    "deep-learning": "deep learning",
    "deeplearning": "deep learning",

    "statistical analysis": "statistics",
    "statistical-analysis": "statistics",
    "statistiques": "statistics",
    "statistique": "statistics",

    "data visualization": "data visualization",
    "data visualisation": "data visualization",

    "powerbi": "power bi",
    "power bi": "power bi",

    "github actions": "github actions",

    "ci cd": "ci/cd",
    "cicd": "ci/cd",

    "restapi": "rest api",
    "rest api": "rest api",

    "api gateway": "api gateway",

    "unit testing": "unit testing",
    "unit tests": "unit testing",
    "tests unitaires": "unit testing",

    "sqlserver": "sql server",
    "sql server": "sql server",

    "microsoft sql server": "sql server",
}


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json_object(content: str) -> str:
    """
    Extracts a JSON object from a model response.

    Supports:
    - Pure JSON
    - ```json ... ```
    - Text before/after the JSON
    """

    if not content:
        return ""

    content = content.strip()

    content = re.sub(
        r"```json\s*",
        "",
        content,
        flags=re.IGNORECASE,
    )

    content = re.sub(
        r"```",
        "",
        content,
    )

    content = content.strip()

    start = content.find("{")

    if start == -1:
        return ""

    end = content.rfind("}")

    if end == -1:
        return content[start:]

    return content[start:end + 1]


# ============================================================
# NORMALIZE LIST
# ============================================================

def normalize_list(value: Any) -> list:
    """
    Returns a clean list.
    """

    if isinstance(value, list):
        return value

    return []


# ============================================================
# CLEAN STRING
# ============================================================

def clean_string(value: Any) -> str | None:
    """
    Cleans a value and returns a string or None.
    """

    if value is None:
        return None

    if not isinstance(value, str):
        return str(value).strip() or None

    value = value.strip()

    if not value:
        return None

    return value


# ============================================================
# CLEAN STRING LIST
# ============================================================

def clean_string_list(values: Any) -> list[str]:
    """
    Cleans a list of strings:
    - removes invalid values
    - removes unnecessary spaces
    - removes duplicates
    """

    if not isinstance(values, list):
        return []

    result = []

    for value in values:

        if not isinstance(value, str):
            continue

        value = value.strip()

        if not value:
            continue

        if value not in result:
            result.append(value)

    return result


# ============================================================
# CLEAN DESCRIPTION
# ============================================================

def clean_description(value: Any) -> str | None:
    """
    Limits descriptions to 30 words.
    """

    value = clean_string(value)

    if not value:
        return None

    words = value.split()

    if len(words) > 30:
        value = " ".join(words[:30])

    return value


# ============================================================
# NORMALIZE SKILL
# ============================================================

def normalize_skill(skill: str) -> str:
    """
    Normalizes a skill name.

    Example:

    SpringBoot
    Spring Boot

    => spring boot
    """

    if not isinstance(skill, str):
        return ""

    skill = skill.lower().strip()

    skill = skill.replace("-", " ")
    skill = skill.replace("_", " ")

    # Remove spaces around important characters
    skill = skill.replace(" . ", ".")
    skill = skill.replace(" / ", "/")

    skill = re.sub(
        r"\s+",
        " ",
        skill,
    )

    # Apply aliases
    if skill in SKILL_ALIASES:
        skill = SKILL_ALIASES[skill]

    return skill.strip()


# ============================================================
# CANONICAL SKILL
# ============================================================

def canonical_skill(skill: str) -> str:
    """
    Returns the canonical form of a skill.
    """

    normalized = normalize_skill(skill)

    return SKILL_ALIASES.get(
        normalized,
        normalized,
    )


# ============================================================
# SKILL IS PRESENT
# ============================================================

def skill_is_present(
    skill: str,
    text: str,
) -> bool:
    """
    Checks if a skill is actually present in the resume text.

    Prevents false matches such as:

    Java -> JavaScript

    And handles special technologies:
    .NET
    C#
    C++
    Node.js
    etc.
    """

    if not skill or not text:
        return False

    skill_normalized = canonical_skill(skill)
    text_normalized = normalize_skill(text)

    if not skill_normalized or not text_normalized:
        return False

    # --------------------------------------------------------
    # Aliases / Variants
    # --------------------------------------------------------

    variants = {
        skill_normalized
    }

    for alias, canonical in SKILL_ALIASES.items():

        if canonical == skill_normalized:
            variants.add(alias)

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    for variant in variants:

        variant = normalize_skill(
            variant
        )

        if not variant:
            continue

        # Technologies containing special characters
        if any(
            char in variant
            for char in [".", "+", "#", "/"]
        ):
            if variant in text_normalized:
                return True

            continue

        # Whole word search
        pattern = rf"\b{re.escape(variant)}\b"

        if re.search(
            pattern,
            text_normalized,
            flags=re.IGNORECASE,
        ):
            return True

    return False


# ============================================================
# EXTRACT ALL RESUME TEXT
# ============================================================

def build_resume_search_text(
    resume_data: ResumeData,
) -> str:
    """
    Builds a global resume text from all available information.

    Used only for skill detection.
    """

    text_parts = []

    # --------------------------------------------------------
    # Personal Info
    # --------------------------------------------------------

    if resume_data.personal_info:

        personal = resume_data.personal_info

        for field in [
            "name",
            "location",
        ]:

            if hasattr(personal, field):

                value = clean_string(
                    getattr(personal, field)
                )

                if value:
                    text_parts.append(value)

    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    for skill in resume_data.skills:

        if isinstance(skill, str):
            text_parts.append(skill)

    # --------------------------------------------------------
    # Experiences
    # --------------------------------------------------------

    for experience in resume_data.experiences:

        for field in [
            "title",
            "company",
            "location",
            "description",
        ]:

            if hasattr(experience, field):

                value = clean_string(
                    getattr(experience, field)
                )

                if value:
                    text_parts.append(value)

    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    for project in resume_data.projects:

        for field in [
            "title",
            "institution",
            "location",
            "description",
        ]:

            if hasattr(project, field):

                value = clean_string(
                    getattr(project, field)
                )

                if value:
                    text_parts.append(value)

    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------

    for education in resume_data.education:

        for field in [
            "degree",
            "institution",
            "location",
            "description",
        ]:

            if hasattr(education, field):

                value = clean_string(
                    getattr(education, field)
                )

                if value:
                    text_parts.append(value)

    # --------------------------------------------------------
    # Certificates
    # --------------------------------------------------------

    for certificate in resume_data.certificates:

        if isinstance(certificate, str):
            text_parts.append(certificate)

    return " ".join(text_parts)


# ============================================================
# EXTRACT SKILLS FROM RESUME DATA
# ============================================================

def collect_resume_skills(
    resume_data: ResumeData,
) -> set[str]:
    """
    Detects only known skills actually present in the resume.
    """

    full_text = build_resume_search_text(
        resume_data
    )

    found_skills = set()

    for skill in REFERENCE_SKILLS:

        if skill_is_present(
            skill,
            full_text,
        ):

            found_skills.add(
                canonical_skill(skill)
            )

    return found_skills


# ============================================================
# GET ROLE SKILLS
# ============================================================

def get_role_skills(
    target_role: str,
) -> list[str]:
    """
    Returns relevant skills for a job position.
    """

    if not target_role:
        return []

    target_role = target_role.strip()

    # Exact match
    if target_role in ROLE_SKILLS:
        return ROLE_SKILLS[target_role]

    # Case-insensitive match
    for role, skills in ROLE_SKILLS.items():

        if role.lower() == target_role.lower():
            return skills

    return []


# ============================================================
# CALCULATE MATCH SCORE
# ============================================================

def calculate_match_score(
    target_role: str,
    detected_resume_skills: set[str],
) -> int:
    """
    Calculates the compatibility score in a fully deterministic way.

    Score = number of role skills present in resume
            / total number of role skills
            × 100

    The AI cannot invent this score.
    """

    role_skills = get_role_skills(
        target_role
    )

    if not role_skills:
        return 0

    role_skills_normalized = [
        canonical_skill(skill)
        for skill in role_skills
    ]

    detected_normalized = {
        canonical_skill(skill)
        for skill in detected_resume_skills
    }

    matched = [
        skill
        for skill in role_skills_normalized
        if skill in detected_normalized
    ]

    score = (
        len(matched)
        / len(role_skills_normalized)
    ) * 100

    return max(
        0,
        min(
            100,
            round(score),
        ),
    )


# ============================================================
# BUILD DETERMINISTIC SKILLS MATCH
# ============================================================

def build_skills_match(
    target_role: str,
    detected_resume_skills: set[str],
) -> list[dict]:
    """
    Builds skills_match on the Python side.

    strong  = present in the resume
    missing = absent from the resume

    This prevents the model from returning:
    Python = missing
    when Python is actually present.
    """

    role_skills = get_role_skills(
        target_role
    )

    if not role_skills:
        return []

    detected_normalized = {
        canonical_skill(skill)
        for skill in detected_resume_skills
    }

    result = []

    for skill in role_skills:

        canonical = canonical_skill(
            skill
        )

        if canonical in detected_normalized:

            status = "strong"

        else:

            status = "missing"

        result.append(
            {
                "skill": skill,
                "status": status,
            }
        )

    return result[:MAX_SKILLS_MATCH]


# ============================================================
# BUILD MISSING SKILLS
# ============================================================

def build_missing_skills(
    target_role: str,
    detected_resume_skills: set[str],
) -> list[str]:
    """
    Builds missing_skills in a deterministic way.
    """

    role_skills = get_role_skills(
        target_role
    )

    detected_normalized = {
        canonical_skill(skill)
        for skill in detected_resume_skills
    }

    missing = []

    for skill in role_skills:

        canonical = canonical_skill(
            skill
        )

        if canonical not in detected_normalized:

            missing.append(skill)

    return missing[:MAX_MISSING_SKILLS]


# ============================================================
# BUILD EXTRACTION PROMPT
# ============================================================

def build_prompt(
    text: str,
    name: str | None,
    email: str | None,
    phone: str | None,
    location: str | None,
) -> str:

    return f"""
You are an expert in automatic resume extraction.

Your mission is to extract only the information present
in the provided resume.

============================================================
CRITICAL RULES
============================================================

- Use only information present in the resume.
- Do not invent any information.
- Do not infer missing information.
- If information is absent, return null.
- If a list is absent, return [].
- Respect exactly the requested JSON format.

Categorization:

- internships and jobs -> experiences
- academic and personal projects -> projects
- degrees and training -> education
- technologies and tools -> skills
- certifications -> certificates

Descriptions must be short and factual.

Limits:

- Maximum 30 skills.
- Maximum 10 experiences.
- Maximum 10 education entries.
- Maximum 10 projects.
- Maximum 10 certifications.

============================================================
DIRECTLY EXTRACTED INFORMATION FROM THE RESUME
============================================================

These information are prioritized:

name:
{json.dumps(name, ensure_ascii=False)}

email:
{json.dumps(email, ensure_ascii=False)}

phone:
{json.dumps(phone, ensure_ascii=False)}

location:
{json.dumps(location, ensure_ascii=False)}

============================================================
MANDATORY FORMAT
============================================================

Return ONLY a valid JSON object.

No markdown.
No explanation.
No text before or after the JSON.

{{
  "personal_info": {{
    "name": null,
    "email": null,
    "phone": null,
    "location": null
  }},

  "skills": [],

  "experiences": [
    {{
      "title": null,
      "company": null,
      "location": null,
      "start_date": null,
      "end_date": null,
      "description": null
    }}
  ],

  "education": [
    {{
      "degree": null,
      "institution": null,
      "location": null,
      "start_date": null,
      "end_date": null,
      "description": null
    }}
  ],

  "projects": [
    {{
      "title": null,
      "institution": null,
      "location": null,
      "start_date": null,
      "end_date": null,
      "description": null
    }}
  ],

  "certificates": []
}}

============================================================
RESUME
============================================================

{text}
"""


# ============================================================
# GROQ REQUEST
# ============================================================

def call_groq(prompt: str):

    """
    Calls Groq with compatibility for versions
    supporting or not supporting reasoning_effort.
    """

    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert resume analysis assistant. "
                "You follow instructions strictly. "
                "You return only valid JSON."
            ),
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    try:

        return client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0,
            max_tokens=3000,
            reasoning_effort="low",
        )

    except TypeError:

        return client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0,
            max_tokens=3000,
        )


# ============================================================
# PARSE JSON RESPONSE
# ============================================================

def parse_json_response(
    content: str,
) -> dict:
    """
    Parses and validates the model's JSON response.
    """

    json_text = extract_json_object(
        content
    )

    if not json_text:

        raise RuntimeError(
            "Unable to find a JSON object in the AI response."
        )

    try:

        result = json.loads(
            json_text
        )

    except json.JSONDecodeError as e:

        print()
        print("========== INVALID JSON ==========")
        print(json_text)
        print()
        print("JSON ERROR:")
        print(str(e))
        print("==================================")
        print()

        raise RuntimeError(
            "The AI model returned an invalid JSON response."
        )

    if not isinstance(
        result,
        dict,
    ):

        raise RuntimeError(
            "The AI response is not a JSON object."
        )

    return result


# ============================================================
# ANALYZE RESUME
# ============================================================

def analyze_resume(
    text: str,
    name: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    location: str | None = None,
) -> ResumeData:
    """
    First step:

    Resume text
        ↓
    Groq
        ↓
    JSON
        ↓
    cleaning
        ↓
    ResumeData
    """

    text = text or ""

    original_length = len(text)

    if len(text) > MAX_INPUT_CHARS:

        text = text[
            :MAX_INPUT_CHARS
        ]

    print()
    print("========== AI INPUT ==========")
    print("MODEL          :", MODEL)
    print("ORIGINAL CHARS :", original_length)
    print("SENT CHARS     :", len(text))
    print("==============================")
    print()

    prompt = build_prompt(
        text=text,
        name=name,
        email=email,
        phone=phone,
        location=location,
    )

    try:

        response = call_groq(
            prompt
        )

    except Exception as e:

        print()
        print("========== GROQ ERROR ==========")
        print(str(e))
        print("================================")
        print()

        raise RuntimeError(
            f"Error during Groq analysis: {str(e)}"
        )

    if not response.choices:

        raise RuntimeError(
            "Groq returned no choices."
        )

    choice = response.choices[0]

    content = choice.message.content or ""

    finish_reason = choice.finish_reason

    print()
    print("========== GROQ RESPONSE ==========")
    print("MODEL        :", MODEL)
    print("FINISH REASON:", finish_reason)
    print("CONTENT      :", repr(content))

    if hasattr(response, "usage"):

        print(
            "USAGE        :",
            response.usage,
        )

    print("====================================")
    print()

    if not content:

        raise RuntimeError(
            "The AI model returned an empty response. "
            f"finish_reason={finish_reason}"
        )

    try:

        result = parse_json_response(
            content
        )

    except RuntimeError as e:

        if finish_reason == "length":

            raise RuntimeError(
                "The AI response was truncated before the JSON ended. "
                "Reduce the resume content or increase max_tokens."
            )

        raise e

    # ========================================================
    # Personal Info
    # ========================================================

    personal_info = result.get(
        "personal_info",
        {},
    )

    if not isinstance(
        personal_info,
        dict,
    ):

        personal_info = {}

    if name:
        personal_info["name"] = name

    if email:
        personal_info["email"] = email

    if phone:
        personal_info["phone"] = phone

    if location:
        personal_info["location"] = location

    # ========================================================
    # Skills
    # ========================================================

    skills = clean_string_list(
        result.get(
            "skills",
            [],
        )
    )

    skills = skills[
        :MAX_SKILLS
    ]

    # ========================================================
    # Experiences
    # ========================================================

    experiences = normalize_list(
        result.get(
            "experiences",
            [],
        )
    )

    cleaned_experiences = []

    for experience in experiences:

        if not isinstance(
            experience,
            dict,
        ):
            continue

        cleaned_experiences.append(
            {
                "title": clean_string(
                    experience.get(
                        "title"
                    )
                ),

                "company": clean_string(
                    experience.get(
                        "company"
                    )
                ),

                "location": clean_string(
                    experience.get(
                        "location"
                    )
                ),

                "start_date": clean_string(
                    experience.get(
                        "start_date"
                    )
                ),

                "end_date": clean_string(
                    experience.get(
                        "end_date"
                    )
                ),

                "description": clean_description(
                    experience.get(
                        "description"
                    )
                ),
            }
        )

    cleaned_experiences = cleaned_experiences[
        :MAX_EXPERIENCES
    ]

    # ========================================================
    # Education
    # ========================================================

    education = normalize_list(
        result.get(
            "education",
            [],
        )
    )

    cleaned_education = []

    for item in education:

        if not isinstance(
            item,
            dict,
        ):
            continue

        cleaned_education.append(
            {
                "degree": clean_string(
                    item.get(
                        "degree"
                    )
                ),

                "institution": clean_string(
                    item.get(
                        "institution"
                    )
                ),

                "location": clean_string(
                    item.get(
                        "location"
                    )
                ),

                "start_date": clean_string(
                    item.get(
                        "start_date"
                    )
                ),

                "end_date": clean_string(
                    item.get(
                        "end_date"
                    )
                ),

                "description": clean_description(
                    item.get(
                        "description"
                    )
                ),
            }
        )

    cleaned_education = cleaned_education[
        :MAX_EDUCATION
    ]

    # ========================================================
    # Projects
    # ========================================================

    projects = normalize_list(
        result.get(
            "projects",
            [],
        )
    )

    cleaned_projects = []

    for project in projects:

        if not isinstance(
            project,
            dict,
        ):
            continue

        cleaned_projects.append(
            {
                "title": clean_string(
                    project.get(
                        "title"
                    )
                ),

                "institution": clean_string(
                    project.get(
                        "institution"
                    )
                ),

                "location": clean_string(
                    project.get(
                        "location"
                    )
                ),

                "start_date": clean_string(
                    project.get(
                        "start_date"
                    )
                ),

                "end_date": clean_string(
                    project.get(
                        "end_date"
                    )
                ),

                "description": clean_description(
                    project.get(
                        "description"
                    )
                ),
            }
        )

    cleaned_projects = cleaned_projects[
        :MAX_PROJECTS
    ]

    # ========================================================
    # Certificates
    # ========================================================

    certificates = clean_string_list(
        result.get(
            "certificates",
            [],
        )
    )

    certificates = certificates[
        :MAX_CERTIFICATES
    ]

    # ========================================================
    # Pydantic Validation
    # ========================================================

    try:

        resume_data = ResumeData(

            personal_info=PersonalInfo(

                name=clean_string(
                    personal_info.get(
                        "name"
                    )
                ),

                email=clean_string(
                    personal_info.get(
                        "email"
                    )
                ),

                phone=clean_string(
                    personal_info.get(
                        "phone"
                    )
                ),

                location=clean_string(
                    personal_info.get(
                        "location"
                    )
                ),
            ),

            skills=skills,

            experiences=cleaned_experiences,

            education=cleaned_education,

            projects=cleaned_projects,

            certificates=certificates,
        )

    except Exception as e:

        print()
        print("========== PYDANTIC ERROR ==========")
        print(str(e))
        print("====================================")
        print()

        raise RuntimeError(
            f"Error during resume data validation: {str(e)}"
        )

    print()
    print("========== RESUME EXTRACTION SUCCESS ==========")
    print("Skills       :", len(resume_data.skills))
    print("Experiences  :", len(resume_data.experiences))
    print("Education    :", len(resume_data.education))
    print("Projects     :", len(resume_data.projects))
    print("Certificates :", len(resume_data.certificates))
    print("===============================================")
    print()

    return resume_data


# ============================================================
# GENERATE RESUME ANALYSIS
# ============================================================

def generate_resume_analysis(
    resume_data: ResumeData,
    target_role: str | None = None,
) -> ResumeAnalysis:
    """
    Second step:

    ResumeData
        ↓
    deterministic skill detection
        ↓
    deterministic score calculation
        ↓
    Groq for qualitative recommendations
        ↓
    ResumeAnalysis
    """

    # ========================================================
    # Target Role
    # ========================================================

    if not target_role or not target_role.strip():

        raise ValueError(
            "The target job position is required."
        )

    target_role = target_role.strip()

    # ========================================================
    # Check Role
    # ========================================================

    role_skills = get_role_skills(
        target_role
    )

    if not role_skills:

        raise ValueError(
            f"Unsupported position: '{target_role}'. "
            f"Available positions: "
            f"{', '.join(ROLE_SKILLS.keys())}"
        )

    # ========================================================
    # Resume JSON
    # ========================================================

    resume_json = json.dumps(
        resume_data.model_dump(),
        ensure_ascii=False,
        indent=2,
    )

    # ========================================================
    # Detect Resume Skills
    # ========================================================

    detected_resume_skills = collect_resume_skills(
        resume_data
    )

    detected_resume_skills_text = ", ".join(
        sorted(
            detected_resume_skills
        )
    )

    print()
    print("========== DETECTED RESUME SKILLS ==========")
    print(
        detected_resume_skills_text
        or "No reference skills detected."
    )
    print("=============================================")
    print()

    # ========================================================
    # Deterministic Score
    # ========================================================

    match_score = calculate_match_score(
        target_role=target_role,
        detected_resume_skills=detected_resume_skills,
    )

    # ========================================================
    # Deterministic Skills Match
    # ========================================================

    skills_match = build_skills_match(
        target_role=target_role,
        detected_resume_skills=detected_resume_skills,
    )

    # ========================================================
    # Deterministic Missing Skills
    # ========================================================

    missing_skills = build_missing_skills(
        target_role=target_role,
        detected_resume_skills=detected_resume_skills,
    )

    print()
    print("========== CALCULATED MATCH SCORE ==========")
    print("Target role :", target_role)
    print(
        "Role skills :",
        len(role_skills),
    )
    print(
        "Matched     :",
        sum(
            1
            for item in skills_match
            if item["status"] == "strong"
        ),
    )
    print(
        "Missing     :",
        len(missing_skills),
    )
    print("Score       :", match_score)
    print("============================================")
    print()

    # ========================================================
    # Analysis Prompt
    # ========================================================

    prompt = f"""
You are an expert technical recruiter and resume analyst.

Analyze the following resume against the position:

============================================================
TARGET POSITION
============================================================

{target_role}

============================================================
EXPECTED SKILLS FOR THIS POSITION
============================================================

{json.dumps(role_skills, ensure_ascii=False)}

============================================================
SKILLS AUTOMATICALLY DETECTED IN THE RESUME
============================================================

{detected_resume_skills_text}

IMPORTANT:

These skills were detected directly from the resume.

They are considered present.

They must NEVER be presented as missing.

============================================================
RESUME DATA
============================================================

{resume_json}

============================================================
OBJECTIVE
============================================================

Produce only the following qualitative elements:

1. strengths
2. recommendations
3. cv_improvements

The score, missing_skills, and skills_match are calculated
by the system and MUST NOT be recalculated by you.

============================================================
RULES
============================================================

1. USE ONLY THE RESUME

Never invent:

- a skill
- an experience
- a project
- an education entry
- a certification
- a technology

============================================================
2. STRENGTHS
============================================================

Maximum 6.

List only strengths actually demonstrated in the resume.

Be specific.

Example:

"Full stack experience with Angular, Spring Boot and .NET"

============================================================
3. RECOMMENDATIONS
============================================================

Maximum 6.

Give concrete actions to improve the profile
for the target position.

Do not recommend learning a skill already present in the resume.

============================================================
4. CV IMPROVEMENTS
============================================================

Maximum 6.

Focus only on resume improvements:

- dates
- descriptions
- technologies
- results
- projects
- certifications
- presentation

============================================================
MANDATORY FORMAT
============================================================

Return ONLY a valid JSON object.

No markdown.
No explanation.

{{
  "strengths": [],
  "recommendations": [],
  "cv_improvements": []
}}
"""

    # ========================================================
    # GROQ
    # ========================================================

    try:

        response = call_groq(
            prompt
        )

    except Exception as e:

        print()
        print("========== GROQ ANALYSIS ERROR ==========")
        print(str(e))
        print("=========================================")
        print()

        raise RuntimeError(
            f"Error during resume analysis: {str(e)}"
        )

    # ========================================================
    # Response
    # ========================================================

    if not response.choices:

        raise RuntimeError(
            "Groq returned no result for the analysis."
        )

    choice = response.choices[0]

    content = choice.message.content or ""

    finish_reason = choice.finish_reason

    print()
    print("========== RESUME ANALYSIS ==========")
    print("TARGET ROLE   :", target_role)
    print("MODEL         :", MODEL)
    print("FINISH REASON :", finish_reason)
    print("CONTENT       :", repr(content))

    if hasattr(response, "usage"):

        print(
            "USAGE         :",
            response.usage,
        )

    print("=====================================")
    print()

    if not content:

        raise RuntimeError(
            "The AI model returned an empty response."
        )

    # ========================================================
    # Parse
    # ========================================================

    try:

        result = parse_json_response(
            content
        )

    except RuntimeError as e:

        if finish_reason == "length":

            raise RuntimeError(
                "The AI analysis response was truncated. "
                "Reduce the content sent or increase max_tokens."
            )

        raise RuntimeError(
            f"Unable to parse AI analysis: {str(e)}"
        )

    # ========================================================
    # Strengths
    # ========================================================

    strengths = clean_string_list(
        result.get(
            "strengths",
            [],
        )
    )

    strengths = strengths[
        :MAX_STRENGTHS
    ]

    # ========================================================
    # Recommendations
    # ========================================================

    recommendations = clean_string_list(
        result.get(
            "recommendations",
            [],
        )
    )

    recommendations = recommendations[
        :MAX_RECOMMENDATIONS
    ]

    # ========================================================
    # CV Improvements
    # ========================================================

    cv_improvements = clean_string_list(
        result.get(
            "cv_improvements",
            [],
        )
    )

    cv_improvements = cv_improvements[
        :MAX_CV_IMPROVEMENTS
    ]

    # ========================================================
    # Build Result
    # ========================================================

    try:

        analysis = ResumeAnalysis(

            target_role=target_role,

            match_score=match_score,

            strengths=strengths,

            missing_skills=missing_skills,

            skills_match=skills_match,

            recommendations=recommendations,

            cv_improvements=cv_improvements,
        )

    except Exception as e:

        print()
        print("========== ANALYSIS VALIDATION ERROR ==========")
        print(str(e))
        print("===============================================")
        print()

        raise RuntimeError(
            f"Error during analysis validation: {str(e)}"
        )

    # ========================================================
    # Success
    # ========================================================

    print()
    print("========== RESUME ANALYSIS SUCCESS ==========")
    print(
        "Target role       :",
        analysis.target_role,
    )
    print(
        "Match score       :",
        analysis.match_score,
    )
    print(
        "Strengths         :",
        len(analysis.strengths),
    )
    print(
        "Missing skills    :",
        len(analysis.missing_skills),
    )
    print(
        "Skills match      :",
        len(analysis.skills_match),
    )
    print(
        "Recommendations   :",
        len(analysis.recommendations),
    )
    print(
        "CV improvements   :",
        len(analysis.cv_improvements),
    )
    print(
        "============================================="
    )
    print()

    return analysis
