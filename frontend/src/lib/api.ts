import { base } from '$app/paths';
import { auth } from './stores.svelte';
import type {
	AnalysisResult,
	CoverLetterResult,
	InterviewQuestionsResult,
	KeywordOptimizeResult,
	SkillGapResult,
	HistoryEntry,
	HistoryDetail,
	User
} from './types';

// ---------------------------------------------------------------------------
// Helpers — cookie-based auth: no Authorization header needed from browser JS
// ---------------------------------------------------------------------------

async function handleResponse<T>(response: Response): Promise<T> {
	if (!response.ok) {
		const body = await response.json().catch(() => null);
		const detail = body?.detail;
		if (response.status === 413) throw new Error('File is too large. Please upload a smaller file.');
		if (response.status === 401) {
			auth.logout();
			throw new Error('Session expired. Please log in again.');
		}
		throw new Error(
			typeof detail === 'string' ? detail : `Request failed (status ${response.status}).`
		);
	}
	return response.json();
}

function makeFormData(file: File, jobDescription: string): FormData {
	const fd = new FormData();
	fd.append('file', file);
	fd.append('job_description', jobDescription);
	return fd;
}

async function postForm<T>(path: string, body: FormData, signal?: AbortSignal): Promise<T> {
	let response: Response;
	try {
		response = await fetch(`${base}/api${path}`, {
			method: 'POST',
			body,
			signal
		});
	} catch (err) {
		if (err instanceof DOMException && err.name === 'AbortError') throw new Error('Request was cancelled.');
		if (typeof navigator !== 'undefined' && !navigator.onLine) throw new Error('You appear to be offline.');
		throw new Error('Could not reach the server. Make sure the backend is running.');
	}
	return handleResponse<T>(response);
}

async function getJson<T>(path: string): Promise<T> {
	const response = await fetch(`${base}/api${path}`);
	return handleResponse<T>(response);
}

async function deleteReq(path: string): Promise<void> {
	const response = await fetch(`${base}/api${path}`, {
		method: 'DELETE'
	});
	if (!response.ok) {
		const body = await response.json().catch(() => null);
		throw new Error(body?.detail || 'Delete failed');
	}
}

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

const REQUIRED_FIELDS: (keyof AnalysisResult)[] = [
	'ats_score', 'ats_explanation', 'match_score', 'match_explanation',
	'detected_role', 'detected_explanation', 'skills_score', 'keyword_score',
	'experience_score', 'project_score', 'matched_keywords', 'missing_keywords',
	'suggestions', 'weak_points', 'summary'
];

function validateResult(data: unknown): AnalysisResult {
	if (!data || typeof data !== 'object') throw new Error('Invalid response from server');
	const obj = data as Record<string, unknown>;
	for (const field of REQUIRED_FIELDS) {
		if (!(field in obj)) throw new Error(`Missing field in response: ${field}`);
	}
	for (const field of ['detected_explanation', 'matched_keywords', 'missing_keywords', 'suggestions', 'weak_points'] as const) {
		if (!Array.isArray(obj[field])) obj[field] = [];
	}
	for (const field of ['ats_score', 'match_score', 'skills_score', 'keyword_score', 'experience_score', 'project_score'] as const) {
		const val = Number(obj[field]);
		obj[field] = Number.isFinite(val) ? Math.max(0, Math.min(100, Math.round(val))) : 0;
	}
	return obj as unknown as AnalysisResult;
}

// ---------------------------------------------------------------------------
// Core: Resume Analysis
// ---------------------------------------------------------------------------

let currentController: AbortController | null = null;

export async function analyzeResume(file: File, jobDescription: string): Promise<AnalysisResult> {
	if (currentController) currentController.abort();
	currentController = new AbortController();
	const raw = await postForm<unknown>('/upload', makeFormData(file, jobDescription), currentController.signal);
	return validateResult(raw);
}

// ---------------------------------------------------------------------------
// Cover Letter
// ---------------------------------------------------------------------------

export async function generateCoverLetter(file: File, jobDescription: string): Promise<CoverLetterResult> {
	return postForm<CoverLetterResult>('/generate/cover-letter', makeFormData(file, jobDescription));
}

// ---------------------------------------------------------------------------
// Interview Questions
// ---------------------------------------------------------------------------

export async function generateInterviewQuestions(file: File, jobDescription: string): Promise<InterviewQuestionsResult> {
	return postForm<InterviewQuestionsResult>('/generate/interview-questions', makeFormData(file, jobDescription));
}

// ---------------------------------------------------------------------------
// Keyword Optimizer
// ---------------------------------------------------------------------------

export async function optimizeKeywords(file: File, jobDescription: string): Promise<KeywordOptimizeResult> {
	return postForm<KeywordOptimizeResult>('/generate/keyword-optimize', makeFormData(file, jobDescription));
}

// ---------------------------------------------------------------------------
// Skill Gap
// ---------------------------------------------------------------------------

export async function analyzeSkillGap(file: File, jobDescription: string): Promise<SkillGapResult> {
	return postForm<SkillGapResult>('/generate/skill-gap', makeFormData(file, jobDescription));
}

// ---------------------------------------------------------------------------
// Export PDF
// ---------------------------------------------------------------------------

export async function exportPdf(file: File, jobDescription: string): Promise<Blob> {
	const fd = makeFormData(file, jobDescription);
	const response = await fetch(`${base}/api/export/pdf`, {
		method: 'POST',
		body: fd
	});
	if (!response.ok) {
		const body = await response.json().catch(() => null);
		throw new Error(body?.detail || 'PDF export failed');
	}
	return response.blob();
}

// ---------------------------------------------------------------------------
// Profile Parsing (LinkedIn / GitHub)
// ---------------------------------------------------------------------------

export async function parseProfile(url: string, jobDescription: string): Promise<AnalysisResult> {
	const fd = new FormData();
	fd.append('url', url);
	fd.append('job_description', jobDescription);
	const raw = await postForm<unknown>('/parse/profile', fd);
	return validateResult(raw);
}

// ---------------------------------------------------------------------------
// History
// ---------------------------------------------------------------------------

export async function getHistory(): Promise<HistoryEntry[]> {
	return getJson<HistoryEntry[]>('/history');
}

export async function getHistoryDetail(id: string): Promise<HistoryDetail> {
	return getJson<HistoryDetail>(`/history/${id}`);
}

export async function deleteHistoryEntry(id: string): Promise<void> {
	return deleteReq(`/history/${id}`);
}

// ---------------------------------------------------------------------------
// Session Validation — check if httpOnly cookie holds a valid session
// ---------------------------------------------------------------------------

export async function validateSession(): Promise<User | null> {
	try {
		const response = await fetch(`${base}/api/auth/me`);
		if (!response.ok) return null;
		return response.json();
	} catch {
		return null;
	}
}

// ---------------------------------------------------------------------------
// Auth — token is set/cleared via httpOnly cookie by the server proxy
// ---------------------------------------------------------------------------

export async function login(email: string, password: string): Promise<{ user: { id: string; email: string; name: string; username: string } }> {
	const fd = new FormData();
	fd.append('email', email);
	fd.append('password', password);
	return postForm('/auth/login', fd);
}

export async function signup(username: string, email: string, password: string): Promise<{ user: { id: string; email: string; name: string; username: string } }> {
	const fd = new FormData();
	fd.append('username', username);
	fd.append('email', email);
	fd.append('password', password);
	return postForm('/auth/signup', fd);
}

export async function logout(): Promise<void> {
	await fetch(`${base}/api/auth/logout`, { method: 'POST' }).catch(() => {});
}
