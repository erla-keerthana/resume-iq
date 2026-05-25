## Project Overview:
AI Resume Analyzer is a full-stack web application that accepts resumes in any file format,converts them into pdf,extracts text and analyzes the resume based on job description or job role.
It generates ATS score, match score and provides detailed suggestions to improve the resume.

## Objectives:
-Support multiple file formats
-Convert all files to PDF
-Extract clean text from resumes
-Analyze resumes using AI
-Compare with job description or role
-Provide structured and meaingful insights

## Core Features:
-Upload resume (PDF,DOCX,TXT,JPG,PNG)
-Automatic file type detection
-Convert all inputs to PDF
-Extract text from PDF
-Job Description input or job role input
-ATS score calculation
-Match score calculation 
-Skill extraction (matched & missing)
-Professional UI

## Tech Stack:

Frontend:
SvelteKit (Svelte 5)

Backend:
FastAPI (Python)

AI:
Claude API or Ollama

Libraries:
-pdfplumber
-python-docx
-pytesseract
-pillow

## Architecture:

Frontend (SvelteKit)--->Backend API (FastAPI)--->File Processing Layer----->PDF Conversion ----->Text Extraction----->AI Analysis --->JSON Response --->Frontend UI


## WorkFlow:
1.User uploads resume (any format)
2.System detects file type
3.Converts file into PDF
4.Extracts text from PDF
5.User provides job description or role
6.Backend sends data to AI
7.AI analyzes resume
8.Returns structed JSON
9.UI displays results


## AI Output Format:

AI must return only JSON:
{
  "ats_score":number,
  "ats_explanation":string,
  "match_score":number,
  "match_explanation":string,
  "detected_role":string,
  "detected_explation":[],
  "skills_score":number,
  "keyword_score":number,
  "experience_score":number,
  "project_score":number,
  "matched_keywords":[],
  "missing_keywords":[],
  "suggestions":[],
  "weak_points":[],
  "summary":string
}

Rules:
-no extra text
-Always return all fields
-keep JSON clean and valid


## AI Behavior:

-Act like an ATS system
-Analyze resume deeply
-Compare with job description or role
-Focus on skills ,keywords and relevance
-provide structured output only


## UI Requriments

### Landing Page
-Title:ResumeIQ
-Short description
-"Get Started" button
-Clean Centered Layout

### Layout
-Center content(max width~800px)
-Card desgin(White,shadow,rounded)
-Responsive

### Upload
-One "Upload Resume" button
-Drag & drop box
-Hide default file input
-Show selected file name

### Job Input
-Textarea with placeholder
-Rounded + padding

### Analyze Button
-Full width
-Enable only after file select 
-Show "Analyzing..." while loading

### Results
-ATS score (big,bold)
-Match score
-Explanation (why score)
-Skills (tags)
-Missing keywords (red)
-Suggestions(list)

### Design
-Simple colors(white,gray,blue)
-rounded corners
-Good spacing

### UX
-Hover effects
-Loading spinner
-Error message if failed

## Development Guidelines
-Build backend first,then frontend
-Keep functions modular
-Use one function for file processing
-Always convert input to PDF before analysis
-Use Svelte 5 runes($state)
-Keep code simple and readable
-Use `<a href="{base}/path">` with `import { base } from '$app/paths'` for all navigation links
-Never use hardcoded absolute paths like `href="/analyze"` or `goto('/')`
-Frontend API calls route through SvelteKit server-side proxy (`/api/[...path]`) to reach the backend
-Backend runs on port 8001, frontend serves on port 5174 (production)

## Production Deployment
-Server: `http://10.10.0.36:5174`
-Deploy with Docker: `docker compose up -d --build`
-Frontend (SvelteKit + adapter-node) serves on port 5174
-Backend (FastAPI + uvicorn) runs on port 8001 (internal to Docker network)
-Frontend proxies all `/api/*` requests to the backend server-side
-No VS Code proxy or Vite dev server dependency

## Environment Setup
-Primary AI: Groq (ultra-fast LPU inference, free tier)
-Set `GROQ_API_KEY` in `backend/.env` — get a key from https://console.groq.com/keys
-Groq models: `llama-3.3-70b-versatile` (primary), `llama-3.1-8b-instant` (fallback)
-Fallback AI: OpenRouter — set `OPENROUTER_API_KEY` in `backend/.env` if Groq is unavailable
-Set `ALLOWED_ORIGINS=http://10.10.0.36:5174` in `backend/.env`
-Set a strong `JWT_SECRET` in `backend/.env` for production

## Constraints
-must support mutiple file formats
-must convert all files to PDF before processing
-must return structured JSON fromAI
-UI must be clean and professional

## Future  Enhancements
-Resume rewrite feature
-Interview question generator
-Skill gap roadmap
-Downloadable PDF report
-Authentication system (JWT)

## Summary
This project builds a real world AI powered resume analysis system that standardizes input by converting all files to PDF and provides ATS-style evaluation with professional UI.