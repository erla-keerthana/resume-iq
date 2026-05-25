# ResumeIQ

AI-powered resume analyzer that accepts resumes in multiple formats (PDF, DOCX, TXT, JPG, PNG), converts them to PDF, extracts text, and analyzes them against job descriptions using AI. Returns ATS scores, match scores, skill assessments, and improvement suggestions.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | SvelteKit (Svelte 5) with adapter-node |
| Backend | FastAPI (Python 3.11) |
| AI | Groq (primary), OpenRouter (fallback) |
| Database | SQLite via SQLAlchemy |
| Auth | JWT (bcrypt hashing, httpOnly cookies) |
| Deployment | Docker Compose |

## Features

- **ATS Analysis** — Score your resume against a job description (0-100)
- **Cover Letter Generator** — AI-written cover letters tailored to your resume + JD
- **Interview Prep** — Technical, behavioral, and situational questions
- **Keyword Optimizer** — Find missing ATS keywords and suggested phrases
- **Skill Gap Analysis** — Identify gaps with a learning roadmap
- **Profile Parsing** — Analyze LinkedIn/GitHub profiles
- **PDF Export** — Download styled analysis reports
- **History Dashboard** — Track past analyses with stats

## Prerequisites

- Docker and Docker Compose (for production)
- Python 3.11+ and Node.js 20+ (for local development)
- A Groq API key (free tier at https://console.groq.com/keys)

## Environment Variables

### Backend (`backend/.env`)

Copy from the template and fill in your values:

```bash
cp backend/.env.example backend/.env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes* | Primary AI provider (free at https://console.groq.com/keys) |
| `OPENROUTER_API_KEY` | No | Fallback AI (https://openrouter.ai/keys) |
| `JWT_SECRET` | Yes | Strong random secret for auth tokens |
| `ALLOWED_ORIGINS` | Yes | Comma-separated CORS origins (e.g. `http://localhost:5174`) |
| `PORT` | No | Backend port (default: `8001`) |
| `DATABASE_URL` | No | SQLAlchemy DB URL (default: `sqlite:///./resumeiq.db`) |

*At least one of `GROQ_API_KEY` or `OPENROUTER_API_KEY` is required.

### Docker Compose

| Variable | Description |
|----------|-------------|
| `PUBLIC_URL` | Public URL of the frontend (default: `http://localhost:5174`). Used for CORS and SvelteKit ORIGIN. |

## Docker Deployment (Production)

```bash
# 1. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys and a strong JWT_SECRET

# 2. Build and start
docker compose up -d --build

# 3. For a custom domain/IP:
PUBLIC_URL=http://your-server:5174 docker compose up -d --build
```

The frontend serves on port **5174** and proxies API requests to the backend internally.

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env (see Environment Variables above)
cp .env.example .env

# Start the server
uvicorn main:app --reload --port 8001
```

### Frontend

```bash
cd frontend
npm install

# Start dev server (proxies /api to backend on port 8001)
BACKEND_URL=http://localhost:8001 npm run dev
```

### Running Tests

```bash
cd backend
pip install pytest httpx
pytest tests/ -v
```

## Architecture

```
Browser → SvelteKit (port 5174) → FastAPI (port 8001) → AI Provider (Groq/OpenRouter)
                                        ↓
                                  File Processing
                                  (PDF conversion → text extraction)
                                        ↓
                                  SQLite (history)
```

- The SvelteKit server acts as a reverse proxy, forwarding `/api/*` requests to the FastAPI backend
- Auth tokens are stored in httpOnly cookies managed by the SvelteKit proxy layer
- All file uploads are converted to PDF before text extraction
- AI analysis uses Groq (fast) with OpenRouter as fallback

## Usage

1. Create an account or sign in
2. Navigate to **Analyze**
3. Upload a resume (PDF, DOCX, TXT, JPG, PNG — max 10 MB)
4. Enter a job description or job role
5. Choose a workflow tab (ATS Analysis, Cover Letter, etc.)
6. Click **Analyze** and review results
7. View past analyses in the **Dashboard**
