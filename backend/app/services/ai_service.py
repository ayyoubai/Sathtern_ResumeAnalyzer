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
    "openai/gpt-oss-20b"
)


# ============================================================
# LIMITS
# ============================================================

MAX_INPUT_CHARS = 7000

MAX_SKILLS = 30
MAX_EXPERIENCES = 10
MAX_EDUCATION = 10
MAX_PROJECTS = 10
MAX_CERTIFICATES = 10


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json_object(content: str) -> str:
    """
    Extrait proprement le premier objet JSON de la réponse IA.

    Supporte :
    - JSON pur
    - ```json ... ```
    - texte avant/après le JSON
    """

    if not content:
        return ""

    content = content.strip()

    # Supprimer les blocs markdown
    content = re.sub(
        r"```json\s*",
        "",
        content,
        flags=re.IGNORECASE
    )

    content = re.sub(
        r"```",
        "",
        content
    )

    content = content.strip()

    start = content.find("{")

    if start == -1:
        return ""

    # Recherche du dernier objet complet
    end = content.rfind("}")

    if end == -1:
        return content[start:]

    return content[start:end + 1]


# ============================================================
# NORMALIZE LIST
# ============================================================

def normalize_list(value: Any) -> list:
    if isinstance(value, list):
        return value

    return []


# ============================================================
# CLEAN STRING
# ============================================================

def clean_string(value: Any) -> str | None:

    if value is None:
        return None

    if not isinstance(value, str):
        return str(value)

    value = value.strip()

    if not value:
        return None

    return value


# ============================================================
# CLEAN STRING LIST
# ============================================================

def clean_string_list(values: Any) -> list[str]:

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

    value = clean_string(value)

    if not value:
        return None

    # Protection contre les descriptions énormes
    words = value.split()

    if len(words) > 30:
        value = " ".join(words[:30])

    return value


# ============================================================
# BUILD PROMPT
# ============================================================

def build_prompt(
    text: str,
    name: str | None,
    email: str | None,
    phone: str | None,
    location: str | None,
) -> str:

    return f"""
Extrais les informations de ce CV.

Retourne UNIQUEMENT du JSON valide.
Aucune explication.
Aucun markdown.
N'invente aucune information.

RÈGLES :
- stages et emplois -> experiences
- projets -> projects
- diplômes/formations -> education
- technologies -> skills
- certifications -> certificates
- information absente -> null
- liste absente -> []
- descriptions très courtes
- maximum 30 skills
- maximum 10 experiences
- maximum 10 education
- maximum 10 projects
- maximum 10 certificates

IMPORTANT :
Les informations suivantes ont été extraites directement du CV.
Elles sont prioritaires :

name: {json.dumps(name, ensure_ascii=False)}
email: {json.dumps(email, ensure_ascii=False)}
phone: {json.dumps(phone, ensure_ascii=False)}
location: {json.dumps(location, ensure_ascii=False)}

FORMAT :

{{
  "personal_info": {{
    "name": null,
    "email": null,
    "phone": null,
    "location": null
  }},
  "skills": [],
  "experiences": [],
  "education": [],
  "projects": [],
  "certificates": []
}}

experience :

{{
  "title": null,
  "company": null,
  "location": null,
  "start_date": null,
  "end_date": null,
  "description": null
}}

education :

{{
  "degree": null,
  "institution": null,
  "location": null,
  "start_date": null,
  "end_date": null,
  "description": null
}}

project :

{{
  "title": null,
  "institution": null,
  "location": null,
  "start_date": null,
  "end_date": null,
  "description": null
}}

CV :
{text}
"""


# ============================================================
# GROQ REQUEST
# ============================================================

def call_groq(prompt: str):

    try:

        response = client.chat.completions.create(
            model=MODEL,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un extracteur automatique de CV. "
                        "Retourne uniquement un JSON valide. "
                        "N'ajoute aucune explication."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],

            temperature=0,

            # Important pour GPT-OSS
            max_tokens=2500,

            reasoning_effort="low",
        )

        return response

    except TypeError:

        # Compatibilité si reasoning_effort n'est pas accepté
        return client.chat.completions.create(
            model=MODEL,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un extracteur automatique de CV. "
                        "Retourne uniquement un JSON valide."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],

            temperature=0,
            max_tokens=2500,
        )


# ============================================================
# VALIDATE JSON
# ============================================================

def parse_json_response(content: str) -> dict:

    json_text = extract_json_object(content)

    if not json_text:
        raise RuntimeError(
            "Impossible de trouver un objet JSON dans la réponse IA."
        )

    try:

        result = json.loads(json_text)

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

    if not isinstance(result, dict):

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

    # ========================================================
    # INPUT
    # ========================================================

    text = text or ""

    original_length = len(text)

    if len(text) > MAX_INPUT_CHARS:
        text = text[:MAX_INPUT_CHARS]

    print()
    print("========== AI INPUT ==========")
    print("MODEL          :", MODEL)
    print("ORIGINAL CHARS :", original_length)
    print("SENT CHARS     :", len(text))
    print("==============================")
    print()

    # ========================================================
    # PROMPT
    # ========================================================

    prompt = build_prompt(
        text=text,
        name=name,
        email=email,
        phone=phone,
        location=location,
    )

    # ========================================================
    # GROQ
    # ========================================================

    try:

        response = call_groq(prompt)

    except Exception as e:

        print()
        print("========== GROQ ERROR ==========")
        print(str(e))
        print("================================")
        print()

        raise RuntimeError(
            f"Erreur lors de l'analyse Groq : {str(e)}"
        )

    # ========================================================
    # RESPONSE
    # ========================================================

    choice = response.choices[0]

    content = choice.message.content or ""

    finish_reason = choice.finish_reason

    print()
    print("========== GROQ RESPONSE ==========")
    print("MODEL:")
    print(MODEL)
    print()
    print("CONTENT:")
    print(repr(content))
    print()
    print("FINISH REASON:")
    print(finish_reason)
    print()

    if hasattr(response, "usage"):

        print("USAGE:")
        print(response.usage)

    print("====================================")
    print()

    # ========================================================
    # EMPTY
    # ========================================================

    if not content:

        raise RuntimeError(
            "Le modèle IA a retourné une réponse vide. "
            f"finish_reason={finish_reason}"
        )

    # ========================================================
    # LENGTH
    # ========================================================

    if finish_reason == "length":

        print()
        print("========== WARNING ==========")
        print(
            "La réponse Groq a atteint la limite de génération."
        )
        print("=============================")
        print()

        # On tente quand même de parser.
        # Dans certains cas le JSON est complet malgré finish_reason.
        try:

            result = parse_json_response(content)

        except RuntimeError:

            raise RuntimeError(
                "La réponse du modèle IA a été coupée avant "
                "la fin du JSON. "
                "Réduis le contenu du CV ou augmente "
                "la capacité de génération."
            )

    else:

        result = parse_json_response(content)

    # ========================================================
    # PERSONAL INFO
    # ========================================================

    personal_info = result.get(
        "personal_info",
        {}
    )

    if not isinstance(personal_info, dict):
        personal_info = {}

    # Les données extraites par regex sont prioritaires.

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
        result.get("skills", [])
    )

    skills = skills[:MAX_SKILLS]

    # ========================================================
    # EXPERIENCES
    # ========================================================

    experiences = normalize_list(
        result.get("experiences", [])
    )

    cleaned_experiences = []

    for experience in experiences:

        if not isinstance(experience, dict):
            continue

        cleaned_experiences.append(
            {
                "title": clean_string(
                    experience.get("title")
                ),

                "company": clean_string(
                    experience.get("company")
                ),

                "location": clean_string(
                    experience.get("location")
                ),

                "start_date": clean_string(
                    experience.get("start_date")
                ),

                "end_date": clean_string(
                    experience.get("end_date")
                ),

                "description": clean_description(
                    experience.get("description")
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
        result.get("education", [])
    )

    cleaned_education = []

    for item in education:

        if not isinstance(item, dict):
            continue

        cleaned_education.append(
            {
                "degree": clean_string(
                    item.get("degree")
                ),

                "institution": clean_string(
                    item.get("institution")
                ),

                "location": clean_string(
                    item.get("location")
                ),

                "start_date": clean_string(
                    item.get("start_date")
                ),

                "end_date": clean_string(
                    item.get("end_date")
                ),

                "description": clean_description(
                    item.get("description")
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
        result.get("projects", [])
    )

    cleaned_projects = []

    for project in projects:

        if not isinstance(project, dict):
            continue

        cleaned_projects.append(
            {
                "title": clean_string(
                    project.get("title")
                ),

                "institution": clean_string(
                    project.get("institution")
                ),

                "location": clean_string(
                    project.get("location")
                ),

                "start_date": clean_string(
                    project.get("start_date")
                ),

                "end_date": clean_string(
                    project.get("end_date")
                ),

                "description": clean_description(
                    project.get("description")
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
        result.get("certificates", [])
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
                    personal_info.get("name")
                ),

                email=clean_string(
                    personal_info.get("email")
                ),

                phone=clean_string(
                    personal_info.get("phone")
                ),

                location=clean_string(
                    personal_info.get("location")
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

    # ========================================================
    # SUCCESS
    # ========================================================

    print()
    print("========== AI ANALYSIS SUCCESS ==========")
    print(
        "Skills       :",
        len(resume_data.skills)
    )
    print(
        "Experiences  :",
        len(resume_data.experiences)
    )
    print(
        "Education    :",
        len(resume_data.education)
    )
    print(
        "Projects     :",
        len(resume_data.projects)
    )
    print(
        "Certificates :",
        len(resume_data.certificates)
    )
    print("=========================================")
    print()

    return resume_data

# ============================================================
# GENERATE RESUME ANALYSIS
# ============================================================

def generate_resume_analysis(
    resume_data: ResumeData,
    target_role: str | None = None,
) -> ResumeAnalysis:

    # ========================================================
    # TARGET ROLE
    # ========================================================

    target_role = (
        target_role.strip()
        if target_role
        else "Full Stack Developer"
    )

    # ========================================================
    # RESUME DATA
    # ========================================================

    resume_json = json.dumps(
        resume_data.model_dump(),
        ensure_ascii=False,
        indent=2
    )

    # ========================================================
    # ANALYSIS PROMPT
    # ========================================================

    prompt = f"""
Analyse ce CV par rapport au poste ciblé.

POSTE CIBLÉ :
{target_role}

DONNÉES DU CV :
{resume_json}

OBJECTIF :
Évalue la compatibilité entre le CV et le poste ciblé.

IMPORTANT :
- Base-toi uniquement sur les informations présentes dans le CV.
- N'invente aucune compétence, expérience ou formation.
- Une compétence absente du CV peut être proposée comme compétence manquante.
- Le score doit être un entier entre 0 et 100.
- Sois réaliste pour un profil junior.
- Ne pénalise pas le candidat simplement parce qu'il ne possède pas toutes
  les technologies possibles du métier.
- Prends en compte les compétences, expériences et projets.
- Les recommandations doivent être concrètes et utiles.
- Les descriptions doivent être courtes.
- Retourne UNIQUEMENT du JSON valide.
- Aucun markdown.
- Aucune explication avant ou après le JSON.

FORMAT OBLIGATOIRE :

{{
  "target_role": "{target_role}",
  "match_score": 0,

  "strengths": [],

  "missing_skills": [],

  "skills_match": [
    {{
      "skill": "",
      "status": ""
    }}
  ],

  "recommendations": [],

  "cv_improvements": []
}}

RÈGLES POUR skills_match :

status doit être exactement l'une de ces valeurs :

- "strong" : compétence clairement présente et pertinente
- "partial" : compétence proche ou partiellement démontrée
- "missing" : compétence importante pour le poste mais absente du CV

Analyse maintenant le CV.
"""

    # ========================================================
    # GROQ
    # ========================================================

    try:

        response = call_groq(prompt)

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

    choice = response.choices[0]

    content = choice.message.content or ""

    finish_reason = choice.finish_reason

    print()
    print("========== RESUME ANALYSIS ==========")
    print("TARGET ROLE    :", target_role)
    print("MODEL          :", MODEL)
    print("FINISH REASON  :", finish_reason)
    print("CONTENT        :", repr(content))
    print("=====================================")
    print()

    if not content:

        raise RuntimeError(
            "Le modèle IA a retourné une réponse vide."
        )

    # ========================================================
    # PARSE JSON
    # ========================================================

    try:

        result = parse_json_response(content)

    except RuntimeError as e:

        raise RuntimeError(
            f"Impossible de parser l'analyse IA : {str(e)}"
        )

    # ========================================================
    # NORMALIZE SCORE
    # ========================================================

    try:

        match_score = int(
            result.get("match_score", 0)
        )

    except (TypeError, ValueError):

        match_score = 0

    match_score = max(
        0,
        min(100, match_score)
    )

    # ========================================================
    # NORMALIZE STRENGTHS
    # ========================================================

    strengths = clean_string_list(
        result.get("strengths", [])
    )

    # ========================================================
    # NORMALIZE MISSING SKILLS
    # ========================================================

    missing_skills = clean_string_list(
        result.get("missing_skills", [])
    )

    # ========================================================
    # NORMALIZE SKILLS MATCH
    # ========================================================

    skills_match = []

    raw_skills_match = result.get(
        "skills_match",
        []
    )

    if isinstance(raw_skills_match, list):

        for item in raw_skills_match:

            if not isinstance(item, dict):
                continue

            skill = clean_string(
                item.get("skill")
            )

            status = clean_string(
                item.get("status")
            )

            if not skill:
                continue

            if status not in {
                "strong",
                "partial",
                "missing"
            }:
                status = "partial"

            skills_match.append(
                {
                    "skill": skill,
                    "status": status
                }
            )

    # ========================================================
    # NORMALIZE RECOMMENDATIONS
    # ========================================================

    recommendations = clean_string_list(
        result.get("recommendations", [])
    )

    # ========================================================
    # NORMALIZE CV IMPROVEMENTS
    # ========================================================

    cv_improvements = clean_string_list(
        result.get("cv_improvements", [])
    )

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
    print("Target role       :", analysis.target_role)
    print("Match score       :", analysis.match_score)
    print("Strengths         :", len(analysis.strengths))
    print("Missing skills    :", len(analysis.missing_skills))
    print("Skills match      :", len(analysis.skills_match))
    print("Recommendations   :", len(analysis.recommendations))
    print("CV improvements   :", len(analysis.cv_improvements))
    print("=============================================")
    print()

    return analysis