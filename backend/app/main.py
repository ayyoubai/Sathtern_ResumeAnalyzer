import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from io import BytesIO
from pypdf import PdfReader
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.parser import (
    clean_extracted_text,
    extract_email,
    extract_phone,
    extract_name,
    extract_location
)
from app.schemas import AnalyzeRequest
from app.services.ai_service import (
    analyze_resume,
    generate_resume_analysis
)
# ============================================================
# APPLICATION
# ============================================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# IN-MEMORY RESUME STORE
# ============================================================
#
# NOTE: stockage en memoire uniquement (pas de DB).
# Suffisant pour un usage internship / demo, mais les donnees
# sont perdues au redemarrage du serveur et non partagees entre
# plusieurs workers/instances.
#
# A remplacer par Redis/DB si deploiement multi-instance.
# ============================================================

resume_store: dict[str, dict] = {}


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# ============================================================
# RESUME UPLOAD
# ============================================================

@app.post("/api/resume/upload")
async def upload_resume(
    file: UploadFile = File(...)
):

    # ========================================================
    # READ FILE
    # ========================================================

    contents = await file.read()

    # ========================================================
    # READ PDF
    # ========================================================

    pdf = PdfReader(
        BytesIO(contents)
    )

    text = ""

    for page in pdf.pages:

        page_text = page.extract_text()

        if page_text:

            text += page_text + "\n"

    # ========================================================
    # CLEAN TEXT
    # ========================================================

    clean_text = clean_extracted_text(
        text
    )

    # ========================================================
    # REGEX EXTRACTION
    # ========================================================

    name = extract_name(
        clean_text
    )

    email = extract_email(
        clean_text
    )

    phone = extract_phone(
        clean_text
    )

    location = extract_location(
        clean_text
    )

    # ========================================================
    # DEBUG
    # ========================================================

    print()
    print("========== EXTRACTED INFO ==========")
    print("NAME     :", name)
    print("EMAIL    :", email)
    print("PHONE    :", phone)
    print("LOCATION :", location)
    print("====================================")
    print()

    # ========================================================
    # AI ANALYSIS
    # ========================================================

    resume_data = analyze_resume(

        clean_text,

        name=name,

        email=email,

        phone=phone,

        location=location
    )

    # ========================================================
    # STORE FOR LATER ANALYSIS
    # ========================================================

    resume_id = str(uuid.uuid4())

    resume_store[resume_id] = {
        "text": clean_text,
        "data": resume_data,
    }

    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "resume_id": resume_id,

        "filename": file.filename,

        "content_type": file.content_type,

        "pages": len(pdf.pages),

        "text": clean_text,

        "data": {

            **resume_data.model_dump(),

            "personal_info": {

                "name": name,

                "email": email,

                "phone": phone,

                "location": location
            }
        }
    }


# ============================================================
# RESUME ANALYSIS (SKILLS + FEEDBACK)
# ============================================================
#
# A appeler APRES /api/resume/upload, avec le resume_id
# retourne par cet endpoint.
#
# Body optionnel : {"target_role": "Data Analyst"}
# Si omis, le domaine est detecte automatiquement par l'IA
# a partir du contenu du CV.
# ============================================================

@app.post("/api/resume/analyze/{resume_id}")
async def analyze_resume_endpoint(
    resume_id: str,
    payload: AnalyzeRequest | None = None
):

    stored = resume_store.get(resume_id)

    if not stored:

        raise HTTPException(
            status_code=404,
            detail="Resume introuvable. Uploadez d'abord un CV via /api/resume/upload."
        )

    target_role = payload.target_role if payload else None

    analysis = generate_resume_analysis(
        stored["data"],
        target_role=target_role,
    )

    return {

        "resume_id": resume_id,

        "analysis": analysis.model_dump(),
    }