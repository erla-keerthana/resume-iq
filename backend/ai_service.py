import json
import os
import re
import time

import requests
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Provider configuration – Groq is primary (ultra-fast LPU), OpenRouter fallback
# ---------------------------------------------------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Groq free-tier models (fastest inference available)
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
    "mixtral-8x7b-32768",
]

# OpenRouter free models (fallback)
OPENROUTER_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-4-31b-it:free",
    "qwen/qwen3-coder:free",
]

SYSTEM_PROMPT = """You are an expert ATS (Applicant Tracking System) resume analyzer.
Analyze the given resume text against the job description.
You must return ONLY valid JSON with no extra text, no markdown, no explanation.

Required JSON format:
{
  "ats_score": <number 0-100>,
  "ats_explanation": "<string>",
  "match_score": <number 0-100>,
  "match_explanation": "<string>",
  "detected_role": "<string>",
  "detected_explanation": ["<string>", ...],
  "skills_score": <number 0-100>,
  "keyword_score": <number 0-100>,
  "experience_score": <number 0-100>,
  "project_score": <number 0-100>,
  "matched_keywords": ["<string>", ...],
  "missing_keywords": ["<string>", ...],
  "suggestions": ["<string>", ...],
  "weak_points": ["<string>", ...],
  "summary": "<string>"
}

Rules:
- Always return ALL fields
- All scores are 0-100
- Keep JSON clean and valid
- No extra text outside JSON
- Analyze deeply: skills, keywords, experience, projects, relevance
"""


def _call_api(url: str, api_key: str, model: str, messages: list) -> requests.Response:
    """Call an OpenAI-compatible chat completions endpoint."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"model": model, "messages": messages}
    return requests.post(url, headers=headers, json=payload, timeout=60)


def _parse_response(resp: requests.Response, model: str):
    """Parse a chat-completions response.  Returns (text, error_string)."""
    if resp.status_code == 401:
        return None, "API key is invalid or expired"
    if resp.status_code == 429:
        return None, f"Model '{model}' is rate-limited"
    if resp.status_code == 404:
        return None, f"Model '{model}' not found"
    if resp.status_code >= 400:
        return None, f"Model '{model}' returned HTTP {resp.status_code}"

    data = resp.json()
    if data.get("error"):
        return None, data["error"].get("message", str(data["error"]))

    choices = data.get("choices")
    if not choices:
        return None, "No response from AI model"

    raw_text = choices[0]["message"]["content"].strip()
    # Strip <think>…</think> blocks (some models include reasoning)
    raw_text = re.sub(r"<think>[\s\S]*?</think>", "", raw_text).strip()
    return raw_text, None


def _extract_json(raw_text: str):
    """Try to extract valid JSON from raw model output."""
    # Remove markdown fences
    if raw_text.startswith("```"):
        lines = raw_text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        raw_text = "\n".join(lines)

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", raw_text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


# ---------------------------------------------------------------------------
# Provider iterators
# ---------------------------------------------------------------------------

def _providers():
    """Yield (url, api_key, model) tuples – Groq first, then OpenRouter."""
    if GROQ_API_KEY:
        for m in GROQ_MODELS:
            yield GROQ_URL, GROQ_API_KEY, m
    if OPENROUTER_API_KEY:
        for m in OPENROUTER_MODELS:
            yield OPENROUTER_URL, OPENROUTER_API_KEY, m


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_resume(resume_text: str, job_description: str) -> dict:
    """Analyze a resume with AI.  Tries Groq first (fast), then OpenRouter."""
    if not GROQ_API_KEY and not OPENROUTER_API_KEY:
        raise ValueError(
            "No AI API key configured. Set GROQ_API_KEY or OPENROUTER_API_KEY in .env"
        )

    user_message = (
        f"Resume Text:\n{resume_text}\n\n"
        f"Job Description:\n{job_description}\n\n"
        "Analyze this resume against the job description. Return ONLY JSON."
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    last_error = None
    for url, key, model in _providers():
        try:
            resp = _call_api(url, key, model, messages)
        except requests.exceptions.Timeout:
            last_error = f"Model '{model}' timed out"
            continue
        except requests.exceptions.ConnectionError:
            last_error = f"Cannot reach {'Groq' if 'groq' in url else 'OpenRouter'} API"
            continue

        raw_text, err = _parse_response(resp, model)
        if err:
            last_error = err
            if resp.status_code == 401:
                # Bad key – skip all models for this provider
                break
            if resp.status_code == 429:
                time.sleep(1)
            continue

        result = _extract_json(raw_text)
        if result:
            return result

        last_error = f"Model '{model}' returned invalid JSON"
        continue

    raise ValueError(
        f"All AI models are currently unavailable. Last error: {last_error}. "
        "Please try again in a few minutes."
    )


# ---------------------------------------------------------------------------
# Reusable helpers
# ---------------------------------------------------------------------------

def _call_ai_text(system_prompt: str, user_prompt: str) -> str:
    """Call AI with fallback and return raw text."""
    if not GROQ_API_KEY and not OPENROUTER_API_KEY:
        raise ValueError("No AI API key configured.")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    last_error = None
    for url, key, model in _providers():
        try:
            resp = _call_api(url, key, model, messages)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            last_error = f"Model '{model}' unreachable"
            continue

        raw_text, err = _parse_response(resp, model)
        if err:
            last_error = err
            if resp.status_code == 401:
                break
            if resp.status_code == 429:
                time.sleep(1)
            continue

        return raw_text

    raise ValueError(f"All AI models unavailable. Last error: {last_error}")


def _call_ai_json(system_prompt: str, user_prompt: str) -> dict:
    """Call AI and parse response as JSON."""
    raw = _call_ai_text(system_prompt, user_prompt)
    result = _extract_json(raw)
    if result:
        return result
    raise ValueError("AI returned invalid JSON")


# ---------------------------------------------------------------------------
# Cover Letter Generator
# ---------------------------------------------------------------------------

COVER_LETTER_PROMPT = """You are a professional cover letter writer.
Write a compelling, personalized cover letter based on the resume and job description.
The letter should:
- Be professional and engaging
- Highlight relevant experience from the resume
- Address key requirements from the job description
- Be 3-4 paragraphs
- Include [Your Name] as placeholder for the name
Return ONLY the cover letter text, no extra commentary."""


def generate_cover_letter(resume_text: str, job_description: str) -> str:
    user_msg = (
        f"Resume:\n{resume_text}\n\n"
        f"Job Description:\n{job_description}\n\n"
        "Write a professional cover letter for this job application."
    )
    return _call_ai_text(COVER_LETTER_PROMPT, user_msg)


# ---------------------------------------------------------------------------
# Interview Questions Generator
# ---------------------------------------------------------------------------

INTERVIEW_PROMPT = """You are an expert interviewer and career coach.
Generate interview questions based on the resume and job description.
Return ONLY valid JSON with no extra text:
{
  "technical": ["question1", "question2", ...],
  "behavioral": ["question1", "question2", ...],
  "situational": ["question1", "question2", ...],
  "tips": ["tip1", "tip2", ...]
}
Generate 5 questions per category and 3-5 tips."""


def generate_interview_questions(resume_text: str, job_description: str) -> dict:
    user_msg = (
        f"Resume:\n{resume_text}\n\n"
        f"Job Description:\n{job_description}\n\n"
        "Generate targeted interview questions. Return ONLY JSON."
    )
    return _call_ai_json(INTERVIEW_PROMPT, user_msg)


# ---------------------------------------------------------------------------
# Keyword Optimizer
# ---------------------------------------------------------------------------

KEYWORD_PROMPT = """You are an ATS keyword optimization expert.
Analyze the resume against the job description and provide keyword optimization.
Return ONLY valid JSON:
{
  "optimized_keywords": ["keyword1", ...],
  "keyword_density": {"keyword": count, ...},
  "missing_critical": ["keyword1", ...],
  "suggested_phrases": ["phrase to add to resume", ...],
  "sections_to_improve": [{"section": "name", "suggestion": "what to add"}, ...],
  "overall_keyword_score": <number 0-100>
}"""


def optimize_keywords(resume_text: str, job_description: str) -> dict:
    user_msg = (
        f"Resume:\n{resume_text}\n\n"
        f"Job Description:\n{job_description}\n\n"
        "Optimize keywords for ATS. Return ONLY JSON."
    )
    return _call_ai_json(KEYWORD_PROMPT, user_msg)


# ---------------------------------------------------------------------------
# Skill Gap Analysis
# ---------------------------------------------------------------------------

SKILL_GAP_PROMPT = """You are a career development expert.
Perform a detailed skill gap analysis comparing the resume to the job requirements.
Return ONLY valid JSON:
{
  "current_skills": ["skill1", ...],
  "required_skills": ["skill1", ...],
  "gap_skills": ["skill1", ...],
  "skill_categories": [
    {"category": "name", "current": ["skill"], "missing": ["skill"], "score": <0-100>}
  ],
  "learning_roadmap": [
    {"skill": "name", "priority": "high|medium|low", "resource": "suggestion", "timeframe": "estimate"}
  ],
  "overall_readiness": <number 0-100>
}"""


def analyze_skill_gap(resume_text: str, job_description: str) -> dict:
    user_msg = (
        f"Resume:\n{resume_text}\n\n"
        f"Job Description:\n{job_description}\n\n"
        "Perform skill gap analysis. Return ONLY JSON."
    )
    return _call_ai_json(SKILL_GAP_PROMPT, user_msg)
