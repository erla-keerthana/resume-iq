export interface AnalysisResult {
	ats_score: number;
	ats_explanation: string;
	match_score: number;
	match_explanation: string;
	detected_role: string;
	detected_explanation: string[];
	skills_score: number;
	keyword_score: number;
	experience_score: number;
	project_score: number;
	matched_keywords: string[];
	missing_keywords: string[];
	suggestions: string[];
	weak_points: string[];
	summary: string;
}

export interface CoverLetterResult {
	cover_letter: string;
}

export interface InterviewQuestionsResult {
	technical: string[];
	behavioral: string[];
	situational: string[];
	tips: string[];
}

export interface KeywordOptimizeResult {
	optimized_keywords: string[];
	keyword_density: Record<string, number>;
	missing_critical: string[];
	suggested_phrases: string[];
	sections_to_improve: { section: string; suggestion: string }[];
	overall_keyword_score: number;
}

export interface SkillGapResult {
	current_skills: string[];
	required_skills: string[];
	gap_skills: string[];
	skill_categories: {
		category: string;
		current: string[];
		missing: string[];
		score: number;
	}[];
	learning_roadmap: {
		skill: string;
		priority: string;
		resource: string;
		timeframe: string;
	}[];
	overall_readiness: number;
}

export interface HistoryEntry {
	id: string;
	filename: string;
	job_description: string;
	ats_score: number;
	match_score: number;
	created_at: string;
}

export interface HistoryDetail extends HistoryEntry {
	result_json: AnalysisResult;
}

export interface User {
	id: string;
	email: string;
	name: string;
	username: string;
}
