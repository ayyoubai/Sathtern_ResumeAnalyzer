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
        f"GROQ_API_KEY introuvable. "
        f"Vérifie le fichier : {ENV_FILE}"
    )

client = Groq(api_key=api_key)

MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)


# ============================================================
# LIMITS
# ============================================================

# On évite de couper trop tôt les CV.
# 12000 caractères reste raisonnable pour l'analyse.
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
    "Statistiques",
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

# Permet d'éviter les faux "missing".
#
# Exemple :
# SpringBoot dans le CV
# Spring Boot dans ROLE_SKILLS
#
# => même compétence.
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
    Extrait un objet JSON depuis une réponse du modèle.

    Supporte :
    - JSON pur
    - ```json ... ```
    - texte avant/après le JSON
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
    Retourne une liste propre.
    """

    if isinstance(value, list):
        return value

    return []


# ============================================================
# CLEAN STRING
# ============================================================

def clean_string(value: Any) -> str | None:
    """
    Nettoie une valeur et retourne une string ou None.
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
    Nettoie une liste de strings :
    - supprime les valeurs invalides
    - supprime les espaces inutiles
    - supprime les doublons
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
    Limite les descriptions à 30 mots.
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
    Normalise une compétence.

    Exemple :

    SpringBoot
    Spring Boot

    => spring boot
    """

    if not isinstance(skill, str):
        return ""

    skill = skill.lower().strip()

    skill = skill.replace("-", " ")
    skill = skill.replace("_", " ")

    # Retirer espaces autour des caractères importants
    skill = skill.replace(" . ", ".")
    skill = skill.replace(" / ", "/")

    skill = re.sub(
        r"\s+",
        " ",
        skill,
    )

    # Appliquer les aliases
    if skill in SKILL_ALIASES:
        skill = SKILL_ALIASES[skill]

    return skill.strip()


# ============================================================
# CANONICAL SKILL
# ============================================================

def canonical_skill(skill: str) -> str:
    """
    Retourne la forme canonique d'une compétence.
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
    Vérifie si une compétence est réellement présente
    dans le texte du CV.

    Évite notamment :

    Java -> JavaScript

    et gère les technologies spéciales :
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
    # ALIASES / VARIANTES
    # --------------------------------------------------------

    variants = {
        skill_normalized
    }

    for alias, canonical in SKILL_ALIASES.items():

        if canonical == skill_normalized:
            variants.add(alias)

    # --------------------------------------------------------
    # Recherche
    # --------------------------------------------------------

    for variant in variants:

        variant = normalize_skill(
            variant
        )

        if not variant:
            continue

        # Technologies contenant des caractères spéciaux
        if any(
            char in variant
            for char in [".", "+", "#", "/"]
        ):
            if variant in text_normalized:
                return True

            continue

        # Recherche par mots complets
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
    Construit un texte global du CV à partir de toutes
    les informations disponibles.

    Utilisé uniquement pour la détection des compétences.
    """

    text_parts = []

    # --------------------------------------------------------
    # PERSONAL INFO
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
    # SKILLS
    # --------------------------------------------------------

    for skill in resume_data.skills:

        if isinstance(skill, str):
            text_parts.append(skill)

    # --------------------------------------------------------
    # EXPERIENCES
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
    # PROJECTS
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
    # EDUCATION
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
    # CERTIFICATES
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
    Détecte uniquement les compétences connues
    présentes réellement dans le CV.
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
    Retourne les compétences pertinentes pour un poste.
    """

    if not target_role:
        return []

    target_role = target_role.strip()

    # Match exact
    if target_role in ROLE_SKILLS:
        return ROLE_SKILLS[target_role]

    # Match insensible à la casse
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
    Calcule le score de compatibilité de manière
    totalement déterministe.

    Score = nombre de compétences du poste présentes
            / nombre total de compétences du poste
            × 100

    L'IA ne peut donc pas inventer le score.
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
    Construit skills_match côté Python.

    strong  = présent dans le CV
    missing = absent du CV

    Cela empêche le modèle de retourner :
    Python = missing
    alors que Python est présent.
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
    Construit missing_skills de manière déterministe.
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
Tu es un expert en extraction automatique de CV.

Ta mission est d'extraire uniquement les informations présentes
dans le CV fourni.

============================================================
RÈGLES CRITIQUES
============================================================

- Utilise uniquement les informations présentes dans le CV.
- N'invente aucune information.
- Ne déduis pas une information absente.
- Si une information est absente, retourne null.
- Si une liste est absente, retourne [].
- Respecte exactement le format JSON demandé.

Catégorisation :

- stages et emplois → experiences
- projets académiques et personnels → projects
- diplômes et formations → education
- technologies et outils → skills
- certifications → certificates

Les descriptions doivent être courtes et factuelles.

Limites :

- Maximum 30 skills.
- Maximum 10 expériences.
- Maximum 10 formations.
- Maximum 10 projets.
- Maximum 10 certifications.

============================================================
INFORMATIONS EXTRAITES DIRECTEMENT DU CV
============================================================

Ces informations sont prioritaires :

name:
{json.dumps(name, ensure_ascii=False)}

email:
{json.dumps(email, ensure_ascii=False)}

phone:
{json.dumps(phone, ensure_ascii=False)}

location:
{json.dumps(location, ensure_ascii=False)}

============================================================
FORMAT OBLIGATOIRE
============================================================

Retourne UNIQUEMENT un objet JSON valide.

Aucun markdown.
Aucune explication.
Aucun texte avant ou après le JSON.

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
CV
============================================================

{text}
"""


# ============================================================
# GROQ REQUEST
# ============================================================

def call_groq(prompt: str):

    """
    Appelle Groq avec compatibilité pour les versions
    supportant ou non reasoning_effort.
    """

    messages = [
        {
            "role": "system",
            "content": (
                "Tu es un expert en analyse de CV. "
                "Tu suis strictement les instructions. "
                "Tu retournes uniquement du JSON valide."
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
    Parse et valide la réponse JSON du modèle.
    """

    json_text = extract_json_object(
        content
    )

    if not json_text:

        raise RuntimeError(
            "Impossible de trouver un objet JSON dans la réponse IA."
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
            "Le modèle IA a retourné un JSON invalide."
        )

    if not isinstance(
        result,
        dict,
    ):

        raise RuntimeError(
            "La réponse IA n'est pas un objet JSON."
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
    Première étape :

    CV texte
        ↓
    Groq
        ↓
    JSON
        ↓
    nettoyage
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
            f"Erreur lors de l'analyse Groq : {str(e)}"
        )

    if not response.choices:

        raise RuntimeError(
            "Groq n'a retourné aucun choix."
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
            "Le modèle IA a retourné une réponse vide. "
            f"finish_reason={finish_reason}"
        )

    try:

        result = parse_json_response(
            content
        )

    except RuntimeError as e:

        if finish_reason == "length":

            raise RuntimeError(
                "La réponse IA a été coupée avant la fin du JSON. "
                "Réduis le contenu du CV ou augmente max_tokens."
            )

        raise e

    # ========================================================
    # PERSONAL INFO
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
    # SKILLS
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
    # EXPERIENCES
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
    # EDUCATION
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
    # PROJECTS
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
    # CERTIFICATES
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
    # PYDANTIC
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
            f"Erreur lors de la validation des données CV : {str(e)}"
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
    Deuxième étape :

    ResumeData
        ↓
    détection déterministe des compétences
        ↓
    calcul déterministe du score
        ↓
    Groq pour les recommandations qualitatives
        ↓
    ResumeAnalysis
    """

    # ========================================================
    # TARGET ROLE
    # ========================================================

    if not target_role or not target_role.strip():

        raise ValueError(
            "Le domaine/poste ciblé est obligatoire."
        )

    target_role = target_role.strip()

    # ========================================================
    # CHECK ROLE
    # ========================================================

    role_skills = get_role_skills(
        target_role
    )

    if not role_skills:

        raise ValueError(
            f"Poste non supporté : '{target_role}'. "
            f"Postes disponibles : "
            f"{', '.join(ROLE_SKILLS.keys())}"
        )

    # ========================================================
    # RESUME JSON
    # ========================================================

    resume_json = json.dumps(
        resume_data.model_dump(),
        ensure_ascii=False,
        indent=2,
    )

    # ========================================================
    # DETECT RESUME SKILLS
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
        or "Aucune compétence de référence détectée."
    )
    print("=============================================")
    print()

    # ========================================================
    # DETERMINISTIC SCORE
    # ========================================================

    match_score = calculate_match_score(
        target_role=target_role,
        detected_resume_skills=detected_resume_skills,
    )

    # ========================================================
    # DETERMINISTIC SKILLS MATCH
    # ========================================================

    skills_match = build_skills_match(
        target_role=target_role,
        detected_resume_skills=detected_resume_skills,
    )

    # ========================================================
    # DETERMINISTIC MISSING SKILLS
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
    # ANALYSIS PROMPT
    # ========================================================

    prompt = f"""
Tu es un expert en recrutement technique et en analyse de CV.

Analyse le CV suivant par rapport au poste :

============================================================
POSTE CIBLÉ
============================================================

{target_role}

============================================================
COMPÉTENCES ATTENDUES POUR CE POSTE
============================================================

{json.dumps(role_skills, ensure_ascii=False)}

============================================================
COMPÉTENCES DÉTECTÉES AUTOMATIQUEMENT DANS LE CV
============================================================

{detected_resume_skills_text}

IMPORTANT :

Ces compétences ont été détectées directement dans le CV.

Elles sont considérées comme présentes.

Elles ne doivent JAMAIS être présentées comme absentes.

============================================================
DONNÉES DU CV
============================================================

{resume_json}

============================================================
OBJECTIF
============================================================

Produis uniquement les éléments qualitatifs suivants :

1. strengths
2. recommendations
3. cv_improvements

Le score, les missing_skills et skills_match sont calculés
par le système et NE DOIVENT PAS être recalculés par toi.

============================================================
RÈGLES
============================================================

1. UTILISER UNIQUEMENT LE CV

N'invente jamais :

- une compétence
- une expérience
- un projet
- une formation
- une certification
- une technologie

============================================================
2. STRENGTHS
============================================================

Maximum 6.

Liste uniquement les points forts réellement démontrés
dans le CV.

Sois précis.

Exemple :

"Expérience full stack avec Angular, Spring Boot et .NET"

============================================================
3. RECOMMENDATIONS
============================================================

Maximum 6.

Donne des actions concrètes pour améliorer le profil
par rapport au poste.

Ne recommande pas comme "à apprendre" une compétence
déjà présente dans le CV.

============================================================
4. CV IMPROVEMENTS
============================================================

Maximum 6.

Concerne uniquement l'amélioration du CV :

- dates
- descriptions
- technologies
- résultats
- projets
- certifications
- présentation

============================================================
FORMAT OBLIGATOIRE
============================================================

Retourne UNIQUEMENT un objet JSON valide.

Aucun markdown.
Aucune explication.

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
            f"Erreur lors de l'analyse du CV : {str(e)}"
        )

    # ========================================================
    # RESPONSE
    # ========================================================

    if not response.choices:

        raise RuntimeError(
            "Groq n'a retourné aucun résultat pour l'analyse."
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
            "Le modèle IA a retourné une réponse vide."
        )

    # ========================================================
    # PARSE
    # ========================================================

    try:

        result = parse_json_response(
            content
        )

    except RuntimeError as e:

        if finish_reason == "length":

            raise RuntimeError(
                "La réponse de l'analyse IA a été coupée. "
                "Réduis le contenu envoyé ou augmente max_tokens."
            )

        raise RuntimeError(
            f"Impossible de parser l'analyse IA : {str(e)}"
        )

    # ========================================================
    # STRENGTHS
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
    # RECOMMENDATIONS
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
    # CV IMPROVEMENTS
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
    # BUILD RESULT
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
            f"Erreur lors de la validation de l'analyse : {str(e)}"
        )

    # ========================================================
    # SUCCESS
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