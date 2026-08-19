# Sathtern Resume Analyzer & AI Chatbot

> AI-powered recruitment assistant for CV analysis, job matching and conversational career assistance.

## 📌 Overview

**Sathtern Resume Analyzer & AI Chatbot** is an AI-powered web application designed to assist candidates and recruiters in analyzing resumes and interacting with an intelligent career chatbot.

The project is developed as a modular application with two main AI features:

1. **Resume Analyzer** — analyzes a candidate's CV according to a selected target position.
2. **AI Chatbot** — provides conversational assistance related to careers, CVs, job applications and professional development.

The main objective is to build a practical AI recruitment assistant capable of combining structured resume analysis with natural-language interaction.

---

# 🎯 Project Objectives

The project aims to:

- Automatically analyze PDF resumes.
- Extract relevant information from resumes.
- Evaluate the compatibility between a resume and a target position.
- Identify candidate strengths.
- Detect missing or insufficient skills.
- Calculate a matching score.
- Estimate confidence regarding the selected role.
- Provide personalized recommendations.
- Suggest improvements to the candidate's CV.
- Provide an AI-powered conversational chatbot.
- Build a clean and scalable architecture that can be extended with additional AI features.

---

# 🧩 Main Features

## 1. Resume Analyzer

The Resume Analyzer allows the user to upload a PDF resume and select a target position.

### Supported target positions

The current application supports several target roles:

- Full Stack Developer
- Frontend Developer
- Backend Developer
- Software Engineer
- DevOps Engineer
- Data Analyst
- Data Scientist
- AI Engineer
- Machine Learning Engineer
- Cybersecurity Engineer

### Analysis workflow

The current workflow is:

```text
User selects a PDF CV
        ↓
Frontend validates the file
        ↓
CV uploaded to backend
        ↓
Backend creates a resume_id
        ↓
User selects target role
        ↓
Frontend sends analysis request
        ↓
AI analyzes the resume
        ↓
Structured analysis returned
        ↓
Frontend displays results
