import uuid
from io import BytesIO

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader

from app.parser import (
    clean_extracted_text,
    extract_email,
    extract_phone,
    extract_name,
    extract_location,
)
from app.schemas import AnalyzeRequest
from app.services.ai_service import (
    analyze_resume,
    generate_resume_analysis,
)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="Sathtern Resume Analyzer API",
    description="AI-powered resume analysis and job matching API.",
    version="1.0.0",
)

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
# NOTE: In-memory storage only (no database).
# Sufficient for internship / demo usage, but data is lost
# on server restart and not shared across workers/instances.
#
# Replace with Redis/DB for multi-instance deployment.
# ============================================================

resume_store: dict[str, dict] = {}


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


# ============================================================
# RESUME UPLOAD
# ============================================================

@app.post("/api/resume/upload")
async def upload_resume(
    file: UploadFile = File(...)
):
    """
    Uploads a PDF resume, extracts text, and performs AI analysis.

    Returns a resume_id to be used with /api/resume/analyze/{resume_id}.
    """

    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # Read file contents
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # Parse PDF
    try:
        pdf = PdfReader(BytesIO(contents))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse PDF: {str(e)}",
        )

    text = ""
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="No text could be extracted from the PDF.",
        )

    # Clean extracted text
    clean_text = clean_extracted_text(text)

    # Regex extraction of basic info
    name = extract_name(clean_text)
    email = extract_email(clean_text)
    phone = extract_phone(clean_text)
    location = extract_location(clean_text)

    # Debug output
    print()
    print("========== EXTRACTED INFO ==========")
    print("NAME     :", name)
    print("EMAIL    :", email)
    print("PHONE    :", phone)
    print("LOCATION :", location)
    print("====================================")
    print()

    # AI analysis
    try:
        resume_data = analyze_resume(
            clean_text,
            name=name,
            email=email,
            phone=phone,
            location=location,
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI analysis failed: {str(e)}",
        )

    # Store for later analysis
    resume_id = str(uuid.uuid4())
    resume_store[resume_id] = {
        "text": clean_text,
        "data": resume_data,
    }

    # Build response
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
                "location": location,
            },
        },
    }


# ============================================================
# RESUME ANALYSIS (SKILLS + FEEDBACK)
# ============================================================
#
# Call AFTER /api/resume/upload, using the resume_id
# returned by that endpoint.
#
# Optional body: {"target_role": "Data Analyst"}
# If omitted, the target role is required and must be provided.
# ============================================================

@app.post("/api/resume/analyze/{resume_id}")
async def analyze_resume_endpoint(
    resume_id: str,
    payload: AnalyzeRequest | None = None,
):
    """
    Analyzes a previously uploaded resume against a target job position.

    Requires a valid resume_id from /api/resume/upload.
    """

    stored = resume_store.get(resume_id)

    if not stored:
        raise HTTPException(
            status_code=404,
            detail="Resume not found. Upload a CV first via /api/resume/upload.",
        )

    target_role = payload.target_role if payload else None

    try:
        analysis = generate_resume_analysis(
            stored["data"],
            target_role=target_role,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI analysis failed: {str(e)}",
        )

    return {
        "resume_id": resume_id,
        "analysis": analysis.model_dump(),
    }
