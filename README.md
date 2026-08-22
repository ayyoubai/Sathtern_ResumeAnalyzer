# Resume Analyzer

AI-powered web application that analyzes a resume (PDF) against a targeted job role using an LLM. Users can upload their resume, select a target position, and receive a compatibility score, strengths, missing skills, and actionable recommendations to improve their resume.

## Features

* Upload resumes in PDF format (drag & drop or manual selection)
* Select a target job role from a list of predefined positions
* Automatic AI-powered analysis using an LLM through Groq
* Overall compatibility score (0–100)
* Detailed overview of strengths, matching skills, and missing skills
* Personalized recommendations and suggestions to improve the resume
* Modern interface with animations, loading indicators, and visual feedback
* New analysis option to easily analyze another resume

## Tech Stack

| Layer             | Technology                      |
| ----------------- | ------------------------------- |
| Frontend          | Angular (standalone components) |
| Backend           | FastAPI (Python)                |
| LLM               | Groq API                        |
| Resume Format     | PDF                             |
| API Communication | REST API                        |

## Architecture

```text
Angular (Frontend)
   │
   │ HTTP (PDF upload + analysis request)
   ▼
FastAPI (Backend)
   │
   │ PDF text extraction
   │ LLM request
   ▼
Groq API
   │
   │ Compatibility score,
   │ strengths, missing skills,
   │ recommendations
   ▼
FastAPI → JSON Response → Angular
                              │
                              ▼
                        Results Display
```

## Prerequisites

Before running the application, make sure you have:

* Node.js 18+ and npm
* Angular CLI

```bash
npm install -g @angular/cli
```

* Python 3.10+
* A Groq API key

You can create a free Groq API key here:

https://console.groq.com/keys

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ayyoubai/Sathtern_ResumeAnalyzer.git
cd Sathtern_ResumeAnalyzer
```

### 2. Backend — FastAPI

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment.

**Windows:**

```bash
venv\Scripts\activate
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file inside the `backend/` directory:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

> The API key can be generated from the Groq Console: https://console.groq.com/keys

Start the FastAPI server:

```bash
uvicorn main:app --reload --port 8000
```

The backend API will be available at:

```text
http://localhost:8000
```

### 3. Frontend — Angular

Open another terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install the dependencies:

```bash
npm install
```

Start the Angular development server:

```bash
ng serve
```

The application will be available at:

```text
http://localhost:4200
```

## Changing the LLM Model

The LLM model is configured through the `GROQ_MODEL` environment variable in the backend `.env` file.

For example:

```env
GROQ_MODEL=llama-3.3-70b-versatile
```

The model can then be loaded in the service responsible for communicating with Groq:

```python
import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

response = client.chat.completions.create(
    model=model,
    messages=[...]
)
```

To change the model, simply update the `GROQ_MODEL` value in your `.env` file.

Available Groq models can be found here:

https://console.groq.com/docs/models

## Usage

1. Open the application at `http://localhost:4200`
2. Upload a resume in PDF format using drag & drop or file selection
3. Select the desired target job role
4. Click **Analyze Resume**
5. Review the compatibility score, strengths, matching skills, missing skills, and recommendations
6. Click **New Analysis** to analyze another resume

## Project Structure

```text
frontend/
└── src/
    └── app/
        ├── core/
        │   ├── models/
        │   │   └── resume-analysis.model.ts
        │   └── services/
        │       ├── resume.service.ts
        │       └── resume-analysis-state.service.ts
        │
        ├── features/
        │   ├── resume-upload/
        │   │   ├── resume-upload.component.ts
        │   │   ├── resume-upload.component.html
        │   │   └── resume-upload.component.scss
        │   │
        │   └── resume-analysis/
        │       ├── resume-analysis.component.ts
        │       ├── resume-analysis.component.html
        │       └── resume-analysis.component.scss
        │
        └── app.routes.ts
```

## Environment Variables

Backend environment variables are defined in `backend/.env`.

| Variable       | Description                        | Example                    |
| -------------- | ---------------------------------- | -------------------------- |
| `GROQ_API_KEY` | Groq API authentication key        | `gsk_xxxxxxxxxxxxxxxxxxxx` |
| `GROQ_MODEL`   | LLM model used for resume analysis | `llama-3.3-70b-versatile`  |

> **Security:** Never commit your `.env` file or expose your Groq API key publicly. Add `.env` to your `.gitignore`.

## How It Works

The application follows a simple AI-powered analysis workflow:

```text
1. User uploads a PDF resume
          ↓
2. Angular sends the file to FastAPI
          ↓
3. FastAPI extracts the resume text
          ↓
4. The extracted content is sent to Groq
          ↓
5. The LLM analyzes the resume
          ↓
6. FastAPI processes the AI response
          ↓
7. Angular displays the analysis results
```
