<script lang="ts">
	import { base } from '$app/paths';
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores.svelte';
	import {
		analyzeResume,
		generateCoverLetter,
		generateInterviewQuestions,
		optimizeKeywords,
		analyzeSkillGap,
		exportPdf,
		parseProfile
	} from '$lib/api';
	import type {
		AnalysisResult,
		CoverLetterResult,
		InterviewQuestionsResult,
		KeywordOptimizeResult,
		SkillGapResult
	} from '$lib/types';
	import { tick, onMount } from 'svelte';

	const ACCEPTED_EXTENSIONS = ['.pdf', '.docx', '.txt', '.jpg', '.jpeg', '.png'];
	const ACCEPTED_TYPES = ACCEPTED_EXTENSIONS.join(',');
	const MAX_FILE_SIZE = 10 * 1024 * 1024;

	type Tab = 'analyze' | 'cover-letter' | 'interview' | 'keywords' | 'skill-gap' | 'profile';
	const TABS: { id: Tab; label: string; icon: string }[] = [
		{ id: 'analyze', label: 'ATS Analysis', icon: 'chart' },
		{ id: 'cover-letter', label: 'Cover Letter', icon: 'letter' },
		{ id: 'interview', label: 'Interview Prep', icon: 'chat' },
		{ id: 'keywords', label: 'Keywords', icon: 'key' },
		{ id: 'skill-gap', label: 'Skill Gap', icon: 'target' },
		{ id: 'profile', label: 'Profile URL', icon: 'link' },
	];

	let activeTab = $state<Tab>('analyze');
	let file = $state<File | null>(null);
	let jobDescription = $state('');
	let loading = $state(false);
	let error = $state('');
	let dragOver = $state(false);
	let profileUrl = $state('');
	let mounted = $state(false);

	// Results
	let analysisResult = $state<AnalysisResult | null>(null);
	let coverLetterResult = $state<CoverLetterResult | null>(null);
	let interviewResult = $state<InterviewQuestionsResult | null>(null);
	let keywordResult = $state<KeywordOptimizeResult | null>(null);
	let skillGapResult = $state<SkillGapResult | null>(null);
	let profileResult = $state<AnalysisResult | null>(null);

	let fileInputEl = $state<HTMLInputElement>(undefined!);
	let resultsEl = $state<HTMLDivElement>(undefined!);

	let canSubmit = $derived(
		activeTab === 'profile'
			? profileUrl.trim().length > 0 && jobDescription.trim().length > 0 && !loading
			: file !== null && jobDescription.trim().length > 0 && !loading
	);

	onMount(() => {
		if (!auth.isLoggedIn) {
			goto(`${base}/login`);
			return;
		}
		requestAnimationFrame(() => { mounted = true; });
	});

	function validateFile(f: File): string | null {
		const ext = '.' + f.name.split('.').pop()?.toLowerCase();
		if (!ACCEPTED_EXTENSIONS.includes(ext)) return `Unsupported file type (${ext}).`;
		if (f.size > MAX_FILE_SIZE) return `File too large (${(f.size / 1024 / 1024).toFixed(1)} MB). Max 10 MB.`;
		if (f.size === 0) return 'File is empty.';
		return null;
	}

	function setFile(f: File) {
		const err = validateFile(f);
		if (err) { error = err; return; }
		file = f;
		error = '';
	}

	function handleFileSelect(e: Event) {
		const input = e.target as HTMLInputElement;
		if (input.files?.[0]) setFile(input.files[0]);
	}

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		dragOver = false;
		const dropped = e.dataTransfer?.files?.[0];
		if (dropped) setFile(dropped);
	}

	function removeFile() {
		file = null;
		error = '';
		if (fileInputEl) fileInputEl.value = '';
	}

	function resetAll() {
		file = null;
		jobDescription = '';
		error = '';
		loading = false;
		profileUrl = '';
		analysisResult = null;
		coverLetterResult = null;
		interviewResult = null;
		keywordResult = null;
		skillGapResult = null;
		profileResult = null;
		if (fileInputEl) fileInputEl.value = '';
		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

	async function handleSubmit() {
		if (!canSubmit) return;
		loading = true;
		error = '';

		try {
			if (activeTab === 'analyze' && file) {
				analysisResult = await analyzeResume(file, jobDescription.trim());
			} else if (activeTab === 'cover-letter' && file) {
				coverLetterResult = await generateCoverLetter(file, jobDescription.trim());
			} else if (activeTab === 'interview' && file) {
				interviewResult = await generateInterviewQuestions(file, jobDescription.trim());
			} else if (activeTab === 'keywords' && file) {
				keywordResult = await optimizeKeywords(file, jobDescription.trim());
			} else if (activeTab === 'skill-gap' && file) {
				skillGapResult = await analyzeSkillGap(file, jobDescription.trim());
			} else if (activeTab === 'profile') {
				profileResult = await parseProfile(profileUrl.trim(), jobDescription.trim());
			}
			await tick();
			resultsEl?.scrollIntoView({ behavior: 'smooth', block: 'start' });
		} catch (e) {
			error = e instanceof Error ? e.message : 'Operation failed. Please try again.';
		} finally {
			loading = false;
		}
	}

	async function handleExportPdf() {
		if (!file || !jobDescription.trim()) return;
		loading = true;
		error = '';
		try {
			const blob = await exportPdf(file, jobDescription.trim());
			const url = URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = 'ResumeIQ_Report.pdf';
			a.click();
			URL.revokeObjectURL(url);
		} catch (e) {
			error = e instanceof Error ? e.message : 'PDF export failed.';
		} finally {
			loading = false;
		}
	}

	function scoreColor(score: number): string {
		if (score >= 80) return 'var(--color-success)';
		if (score >= 60) return 'var(--color-warning)';
		return 'var(--color-danger)';
	}

	function scoreLabel(score: number): string {
		if (score >= 80) return 'Excellent';
		if (score >= 60) return 'Good';
		if (score >= 40) return 'Fair';
		return 'Needs Work';
	}

	function formatFileSize(bytes: number): string {
		if (bytes < 1024) return bytes + ' B';
		if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
		return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
	}

	let hasAnyResult = $derived(
		analysisResult || coverLetterResult || interviewResult || keywordResult || skillGapResult || profileResult
	);

	let buttonLabel = $derived.by(() => {
		if (loading) return 'Processing...';
		const labels: Record<Tab, string> = {
			'analyze': 'Analyze Resume',
			'cover-letter': 'Generate Cover Letter',
			'interview': 'Generate Questions',
			'keywords': 'Optimize Keywords',
			'skill-gap': 'Analyze Skill Gap',
			'profile': 'Analyze Profile',
		};
		return labels[activeTab];
	});

	let copied = $state(false);
	function copyText(text: string) {
		navigator.clipboard.writeText(text);
		copied = true;
		setTimeout(() => { copied = false; }, 2000);
	}
</script>

<svelte:head>
	<title>Analyze - ResumeIQ</title>
	<meta name="description" content="AI-powered resume analysis - ATS scoring, cover letters, interview prep, and more" />
</svelte:head>

<div class="page" class:mounted>
	<!-- Decorative glow -->
	<div class="page-glow page-glow-1"></div>
	<div class="page-glow page-glow-2"></div>

	<main class="container">
		<!-- Page header -->
		<div class="page-header anim-fade-up" style="--delay: 0s">
			<span class="section-tag">AI Analysis</span>
			<h1>Analyze Your <span class="gradient-text">Resume</span></h1>
			<p class="page-subtitle">Upload your resume and paste a job description to get instant AI-powered insights.</p>
		</div>

		<!-- Tabs -->
		<div class="tabs anim-fade-up" style="--delay: 0.1s">
			{#each TABS as tab}
				<button
					class="tab"
					class:active={activeTab === tab.id}
					onclick={() => activeTab = tab.id}
				>
					{#if tab.icon === 'chart'}
						<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
					{:else if tab.icon === 'letter'}
						<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
					{:else if tab.icon === 'chat'}
						<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
					{:else if tab.icon === 'key'}
						<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 7h2a5 5 0 0 1 0 10h-2m-6 0H7A5 5 0 0 1 7 7h2"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
					{:else if tab.icon === 'target'}
						<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
					{:else if tab.icon === 'link'}
						<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
					{/if}
					{tab.label}
				</button>
			{/each}
		</div>

		<!-- Upload Section -->
		{#if activeTab !== 'profile'}
			<section class="card anim-fade-up" style="--delay: 0.15s">
				<div class="card-header">
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
					<div>
						<h2 class="card-title">Upload Resume</h2>
						<p class="card-desc">PDF, DOCX, TXT, JPG, PNG (max 10 MB)</p>
					</div>
				</div>
				<input bind:this={fileInputEl} type="file" accept={ACCEPTED_TYPES} onchange={handleFileSelect} class="sr-only" />
				<div
					class="dropzone"
					class:dragover={dragOver}
					class:has-file={file !== null}
					role="button"
					tabindex="0"
					onclick={() => fileInputEl?.click()}
					onkeydown={(e: KeyboardEvent) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fileInputEl?.click(); }}}
					ondrop={handleDrop}
					ondragover={(e: DragEvent) => { e.preventDefault(); dragOver = true; }}
					ondragleave={() => dragOver = false}
				>
					{#if file}
						<div class="file-info">
							<div class="file-icon-wrap">
								<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
							</div>
							<div class="file-details">
								<span class="file-name">{file.name}</span>
								<span class="file-size">{formatFileSize(file.size)}</span>
							</div>
							<button class="remove-btn" onclick={(e: MouseEvent) => { e.stopPropagation(); removeFile(); }} aria-label="Remove">
								<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
							</button>
						</div>
					{:else}
						<div class="upload-prompt">
							<div class="upload-icon-wrap">
								<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
							</div>
							<p class="drop-text">Drag & drop your resume here</p>
							<p class="drop-sub">or <span class="browse-link">browse files</span></p>
						</div>
					{/if}
				</div>
			</section>
		{:else}
			<!-- Profile URL input -->
			<section class="card anim-fade-up" style="--delay: 0.15s">
				<div class="card-header">
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
					<div>
						<h2 class="card-title">LinkedIn / GitHub Profile</h2>
						<p class="card-desc">Enter a public profile URL to analyze</p>
					</div>
				</div>
				<input
					type="url"
					bind:value={profileUrl}
					placeholder="https://github.com/username or https://linkedin.com/in/username"
					class="text-input"
					disabled={loading}
				/>
			</section>
		{/if}

		<!-- Job Description -->
		<section class="card anim-fade-up" style="--delay: 0.2s">
			<div class="card-header">
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
				<div>
					<h2 class="card-title">Job Description</h2>
					<p class="card-desc">Paste the job description or enter a job role</p>
				</div>
			</div>
			<textarea bind:value={jobDescription} placeholder="e.g. Senior Frontend Developer with 5+ years experience in React, TypeScript..." rows="5" disabled={loading}></textarea>
		</section>

		<!-- Submit + Export buttons -->
		<div class="action-row anim-fade-up" style="--delay: 0.25s">
			<button class="analyze-btn" disabled={!canSubmit} onclick={handleSubmit}>
				{#if loading}<span class="spinner"></span>{/if}
				{buttonLabel}
				{#if !loading}
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
				{/if}
			</button>
			{#if activeTab === 'analyze' && file && jobDescription.trim()}
				<button class="export-btn" disabled={loading} onclick={handleExportPdf} title="Export PDF Report">
					<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
					PDF
				</button>
			{/if}
		</div>

		<!-- Error -->
		{#if error}
			<div class="error-banner" role="alert">
				<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
				</svg>
				<span>{error}</span>
			</div>
		{/if}

		<!-- Results Container -->
		{#if hasAnyResult}
			<div class="results" bind:this={resultsEl}>

				<!-- ATS Analysis Results -->
				{#if analysisResult && activeTab === 'analyze'}
					{@render analysisResults(analysisResult)}
				{/if}

				<!-- Profile Analysis Results -->
				{#if profileResult && activeTab === 'profile'}
					{@render analysisResults(profileResult)}
				{/if}

				<!-- Cover Letter -->
				{#if coverLetterResult && activeTab === 'cover-letter'}
					<section class="card result-card">
						<div class="card-header">
							<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
							<h2 class="card-title">Generated Cover Letter</h2>
						</div>
						<pre class="cover-letter-text">{coverLetterResult.cover_letter}</pre>
						<button class="copy-btn" onclick={() => copyText(coverLetterResult?.cover_letter ?? '')}>
							<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
							{copied ? 'Copied!' : 'Copy to Clipboard'}
						</button>
					</section>
				{/if}

				<!-- Interview Questions -->
				{#if interviewResult && activeTab === 'interview'}
					{#each [
						{ title: 'Technical Questions', items: interviewResult.technical, accent: '#3b82f6' },
						{ title: 'Behavioral Questions', items: interviewResult.behavioral, accent: '#8b5cf6' },
						{ title: 'Situational Questions', items: interviewResult.situational, accent: '#06b6d4' },
					] as section}
						{#if section.items?.length}
							<section class="card result-card" style="--accent: {section.accent}">
								<h2 class="card-title accent-title" style="--accent: {section.accent}">{section.title}</h2>
								<ol class="question-list">
									{#each section.items as q, i}
										<li>
											<span class="q-num">{i + 1}</span>
											<span>{q}</span>
										</li>
									{/each}
								</ol>
							</section>
						{/if}
					{/each}
					{#if interviewResult.tips?.length}
						<section class="card result-card">
							<h2 class="card-title accent-title" style="--accent: #10b981">Interview Tips</h2>
							<ul class="tip-list">
								{#each interviewResult.tips as tip}
									<li>
										<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
										{tip}
									</li>
								{/each}
							</ul>
						</section>
					{/if}
				{/if}

				<!-- Keyword Optimizer -->
				{#if keywordResult && activeTab === 'keywords'}
					<section class="card result-card">
						<div class="score-header-row">
							<h2 class="card-title">Keyword Score</h2>
							<span class="score-pill" style="background: color-mix(in srgb, {scoreColor(keywordResult.overall_keyword_score || 0)} 15%, transparent); color: {scoreColor(keywordResult.overall_keyword_score || 0)}">{keywordResult.overall_keyword_score || 0}/100</span>
						</div>
						<div class="progress-bar"><div class="progress-fill" style="width: {keywordResult.overall_keyword_score || 0}%; background: {scoreColor(keywordResult.overall_keyword_score || 0)}"></div></div>
					</section>
					{#if keywordResult.missing_critical?.length}
						<section class="card result-card">
							<h2 class="card-title accent-title" style="--accent: var(--color-danger)">Missing Critical Keywords</h2>
							<div class="tags">{#each keywordResult.missing_critical as kw}<span class="tag tag-missing">{kw}</span>{/each}</div>
						</section>
					{/if}
					{#if keywordResult.suggested_phrases?.length}
						<section class="card result-card">
							<h2 class="card-title accent-title" style="--accent: var(--color-primary)">Suggested Phrases to Add</h2>
							<ul class="suggestion-list">{#each keywordResult.suggested_phrases as p}<li><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>{p}</li>{/each}</ul>
						</section>
					{/if}
					{#if keywordResult.sections_to_improve?.length}
						<section class="card result-card">
							<h2 class="card-title accent-title" style="--accent: #f59e0b">Sections to Improve</h2>
							{#each keywordResult.sections_to_improve as s}
								<div class="improve-item">
									<strong>{s.section}</strong>
									<p>{s.suggestion}</p>
								</div>
							{/each}
						</section>
					{/if}
				{/if}

				<!-- Skill Gap -->
				{#if skillGapResult && activeTab === 'skill-gap'}
					<section class="card result-card">
						<div class="score-header-row">
							<h2 class="card-title">Overall Readiness</h2>
							<span class="score-pill" style="background: color-mix(in srgb, {scoreColor(skillGapResult.overall_readiness || 0)} 15%, transparent); color: {scoreColor(skillGapResult.overall_readiness || 0)}">{skillGapResult.overall_readiness || 0}%</span>
						</div>
						<div class="progress-bar"><div class="progress-fill" style="width: {skillGapResult.overall_readiness || 0}%; background: {scoreColor(skillGapResult.overall_readiness || 0)}"></div></div>
					</section>
					{#if skillGapResult.gap_skills?.length}
						<section class="card result-card">
							<h2 class="card-title accent-title" style="--accent: var(--color-danger)">Skills to Acquire</h2>
							<div class="tags">{#each skillGapResult.gap_skills as s}<span class="tag tag-missing">{s}</span>{/each}</div>
						</section>
					{/if}
					{#if skillGapResult.skill_categories?.length}
						<section class="card result-card">
							<h2 class="card-title accent-title" style="--accent: #8b5cf6">Skill Categories</h2>
							{#each skillGapResult.skill_categories as cat}
								<div class="sub-score-item">
									<div class="sub-score-header">
										<span>{cat.category}</span>
										<span class="sub-score-val" style="color: {scoreColor(cat.score)}">{cat.score}/100</span>
									</div>
									<div class="progress-bar"><div class="progress-fill" style="width: {cat.score}%; background: {scoreColor(cat.score)}"></div></div>
									{#if cat.missing?.length}
										<div class="tags" style="margin-top:0.5rem">{#each cat.missing as m}<span class="tag tag-missing">{m}</span>{/each}</div>
									{/if}
								</div>
							{/each}
						</section>
					{/if}
					{#if skillGapResult.learning_roadmap?.length}
						<section class="card result-card">
							<h2 class="card-title accent-title" style="--accent: #10b981">Learning Roadmap</h2>
							<div class="roadmap-grid">
								{#each skillGapResult.learning_roadmap as item}
									<div class="roadmap-item">
										<div class="roadmap-header">
											<strong>{item.skill}</strong>
											<span class="priority-badge priority-{item.priority}">{item.priority}</span>
										</div>
										<p class="roadmap-resource">{item.resource}</p>
										<p class="roadmap-time">{item.timeframe}</p>
									</div>
								{/each}
							</div>
						</section>
					{/if}
				{/if}

				<button class="reset-btn" onclick={resetAll}>
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
					Start New Analysis
				</button>
			</div>
		{/if}
	</main>
</div>

<!-- Reusable analysis results snippet -->
{#snippet analysisResults(result: AnalysisResult)}
	<section class="card result-card result-summary">
		<div class="card-header">
			<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
			<h2 class="card-title">Analysis Summary</h2>
		</div>
		{#if result.detected_role}
			<div class="detected-role-badge">
				<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
				{result.detected_role}
			</div>
		{/if}
		<p class="summary-text">{result.summary}</p>
	</section>

	<div class="score-grid">
		{#each [
			{ label: 'ATS Score', score: result.ats_score, explanation: result.ats_explanation, accent: '#3b82f6' },
			{ label: 'Match Score', score: result.match_score, explanation: result.match_explanation, accent: '#8b5cf6' },
		] as card}
			<div class="score-card" style="--accent: {card.accent}">
				<div class="score-ring-wrap">
					<svg class="score-ring" viewBox="0 0 36 36">
						<path class="ring-bg" d="M18 2.0845a 15.9155 15.9155 0 0 1 0 31.831a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke-width="3"/>
						<path class="ring-fill" d="M18 2.0845a 15.9155 15.9155 0 0 1 0 31.831a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke-width="3" stroke-dasharray="{card.score}, 100" style="stroke: {scoreColor(card.score)}"/>
					</svg>
					<span class="score-value" style="color: {scoreColor(card.score)}">{card.score}</span>
				</div>
				<h3>{card.label}</h3>
				<span class="score-badge" style="color: {scoreColor(card.score)}">{scoreLabel(card.score)}</span>
				<p class="score-explanation">{card.explanation}</p>
			</div>
		{/each}
	</div>

	<section class="card result-card">
		<h2 class="card-title accent-title" style="--accent: #8b5cf6">Detailed Scores</h2>
		<div class="sub-scores">
			{#each [
				{ label: 'Skills', value: result.skills_score, icon: 'layers' },
				{ label: 'Keywords', value: result.keyword_score, icon: 'key' },
				{ label: 'Experience', value: result.experience_score, icon: 'briefcase' },
				{ label: 'Projects', value: result.project_score, icon: 'folder' }
			] as item}
				<div class="sub-score-item">
					<div class="sub-score-header">
						<span class="sub-label">
							{#if item.icon === 'layers'}
								<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
							{:else if item.icon === 'key'}
								<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 7h2a5 5 0 0 1 0 10h-2m-6 0H7A5 5 0 0 1 7 7h2"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
							{:else if item.icon === 'briefcase'}
								<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/></svg>
							{:else}
								<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
							{/if}
							{item.label}
						</span>
						<span class="sub-score-val" style="color: {scoreColor(item.value)}">{item.value}/100</span>
					</div>
					<div class="progress-bar"><div class="progress-fill" style="width: {item.value}%; background: {scoreColor(item.value)}"></div></div>
				</div>
			{/each}
		</div>
	</section>

	<div class="keyword-grid">
		<section class="card result-card">
			<h2 class="card-title accent-title" style="--accent: var(--color-success)">Matched Keywords</h2>
			{#if result.matched_keywords.length > 0}
				<div class="tags">{#each result.matched_keywords as kw}<span class="tag tag-matched">{kw}</span>{/each}</div>
			{:else}<p class="empty-text">No matched keywords found</p>{/if}
		</section>
		<section class="card result-card">
			<h2 class="card-title accent-title" style="--accent: var(--color-danger)">Missing Keywords</h2>
			{#if result.missing_keywords.length > 0}
				<div class="tags">{#each result.missing_keywords as kw}<span class="tag tag-missing">{kw}</span>{/each}</div>
			{:else}<p class="empty-text">No missing keywords</p>{/if}
		</section>
	</div>

	{#if result.suggestions.length > 0}
		<section class="card result-card">
			<h2 class="card-title accent-title" style="--accent: var(--color-primary)">Suggestions</h2>
			<ul class="suggestion-list">{#each result.suggestions as s}<li><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>{s}</li>{/each}</ul>
		</section>
	{/if}

	{#if result.weak_points.length > 0}
		<section class="card result-card">
			<h2 class="card-title accent-title" style="--accent: var(--color-warning)">Areas to Improve</h2>
			<ul class="weak-list">{#each result.weak_points as p}<li><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--color-warning)" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>{p}</li>{/each}</ul>
		</section>
	{/if}
{/snippet}

<style>
	.page {
		min-height: 100vh;
		background: var(--color-bg);
		position: relative;
		overflow: hidden;
	}

	/* Decorative glow */
	.page-glow {
		position: fixed;
		border-radius: 50%;
		filter: blur(100px);
		opacity: 0.2;
		pointer-events: none;
		z-index: 0;
	}
	.page-glow-1 {
		width: 500px; height: 500px;
		background: var(--color-primary);
		top: -150px; right: -150px;
		animation: pulse-glow 8s ease-in-out infinite alternate;
	}
	.page-glow-2 {
		width: 400px; height: 400px;
		background: #8b5cf6;
		bottom: -100px; left: -100px;
		animation: pulse-glow 8s ease-in-out infinite alternate 4s;
	}
	@keyframes pulse-glow {
		0% { transform: scale(1); opacity: 0.15; }
		100% { transform: scale(1.2); opacity: 0.25; }
	}

	/* Animations */
	.anim-fade-up {
		opacity: 0;
		transform: translateY(20px);
	}
	.mounted .anim-fade-up {
		animation: fadeUp 0.5s ease forwards;
		animation-delay: var(--delay, 0s);
	}
	@keyframes fadeUp {
		to { opacity: 1; transform: translateY(0); }
	}

	.container {
		max-width: 880px;
		margin: 0 auto;
		padding: 1.5rem 1.5rem 4rem;
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
		position: relative;
		z-index: 1;
	}

	/* Page header */
	.page-header {
		text-align: center;
		padding: 0.5rem 0 0.5rem;
	}
	.section-tag {
		display: inline-block;
		padding: 0.25rem 0.875rem;
		border-radius: var(--radius-full);
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		background: color-mix(in srgb, var(--color-primary) 10%, transparent);
		color: var(--color-primary);
		border: 1px solid color-mix(in srgb, var(--color-primary) 20%, transparent);
		margin-bottom: 0.75rem;
	}
	.page-header h1 {
		font-size: 2rem;
		font-weight: 800;
		color: var(--color-text);
		margin-bottom: 0.5rem;
	}
	.gradient-text {
		background: linear-gradient(135deg, var(--color-primary), #8b5cf6);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}
	.page-subtitle {
		font-size: 0.9375rem;
		color: var(--color-text-muted);
		max-width: 500px;
		margin: 0 auto;
		line-height: 1.6;
	}

	/* Tabs */
	.tabs {
		display: flex;
		gap: 0.375rem;
		overflow-x: auto;
		padding-bottom: 0.25rem;
		scrollbar-width: none;
	}
	.tabs::-webkit-scrollbar { display: none; }
	.tab {
		display: flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.5rem 1rem;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-full);
		background: color-mix(in srgb, var(--color-surface) 80%, transparent);
		backdrop-filter: blur(8px);
		color: var(--color-text-secondary);
		font-size: 0.8125rem;
		font-weight: 600;
		cursor: pointer;
		white-space: nowrap;
		transition: all 0.2s;
	}
	.tab:hover {
		background: var(--color-surface-hover);
		color: var(--color-text);
		border-color: var(--color-text-muted);
	}
	.tab.active {
		background: linear-gradient(135deg, var(--color-primary), #4f46e5);
		color: white;
		border-color: transparent;
		box-shadow: 0 2px 8px color-mix(in srgb, var(--color-primary) 35%, transparent);
	}

	/* Card */
	.card {
		background: color-mix(in srgb, var(--color-surface) 85%, transparent);
		backdrop-filter: blur(12px);
		-webkit-backdrop-filter: blur(12px);
		border-radius: var(--radius-lg);
		padding: 1.5rem;
		box-shadow: var(--shadow-md);
		border: 1px solid color-mix(in srgb, var(--color-border) 60%, transparent);
		transition: border-color 0.2s;
	}
	.card:hover { border-color: var(--color-border); }

	.card-header {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
		margin-bottom: 1rem;
	}
	.card-header svg { flex-shrink: 0; margin-top: 0.125rem; }
	.card-title { font-size: 1rem; font-weight: 700; color: var(--color-text); margin-bottom: 0.125rem; }
	.card-desc { font-size: 0.8125rem; color: var(--color-text-muted); }

	.accent-title {
		padding-left: 0.75rem;
		border-left: 3px solid var(--accent, var(--color-primary));
		margin-bottom: 0.75rem;
	}

	/* Inputs */
	.sr-only { position: absolute; opacity: 0; width: 1px; height: 1px; pointer-events: none; }
	.text-input, textarea {
		width: 100%;
		padding: 0.8125rem 1rem;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		font-family: inherit;
		font-size: 0.875rem;
		color: var(--color-text);
		background: color-mix(in srgb, var(--color-bg) 60%, transparent);
		transition: border-color 0.2s, box-shadow 0.2s;
		line-height: 1.6;
		resize: vertical;
	}
	.text-input:focus, textarea:focus {
		outline: none;
		border-color: var(--color-primary);
		box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-primary) 15%, transparent);
	}
	textarea::placeholder, .text-input::placeholder { color: var(--color-text-muted); }
	textarea:disabled, .text-input:disabled { opacity: 0.6; cursor: not-allowed; }

	/* Dropzone */
	.dropzone {
		border: 2px dashed var(--color-border);
		border-radius: var(--radius-lg);
		padding: 2rem;
		text-align: center;
		cursor: pointer;
		transition: border-color 0.2s, background 0.2s;
	}
	.dropzone:hover, .dropzone:focus-visible, .dropzone.dragover {
		border-color: var(--color-primary);
		background: color-mix(in srgb, var(--color-primary) 5%, transparent);
	}
	.dropzone:focus-visible { outline: none; }
	.dropzone.has-file {
		border-style: solid;
		border-color: var(--color-primary);
		background: color-mix(in srgb, var(--color-primary) 5%, transparent);
		padding: 1rem 1.25rem;
	}

	.upload-prompt { display: flex; flex-direction: column; align-items: center; gap: 0.375rem; }
	.upload-icon-wrap {
		width: 56px; height: 56px;
		border-radius: 16px;
		background: color-mix(in srgb, var(--color-primary) 10%, transparent);
		display: flex; align-items: center; justify-content: center;
		margin-bottom: 0.5rem;
		border: 1px solid color-mix(in srgb, var(--color-primary) 15%, transparent);
	}
	.drop-text { font-size: 0.875rem; font-weight: 600; color: var(--color-text); }
	.drop-sub { font-size: 0.8125rem; color: var(--color-text-muted); }
	.browse-link { color: var(--color-primary); font-weight: 600; text-decoration: underline; }

	.file-info { display: flex; align-items: center; gap: 0.75rem; }
	.file-icon-wrap {
		width: 40px; height: 40px;
		border-radius: 10px;
		background: color-mix(in srgb, var(--color-primary) 10%, transparent);
		display: flex; align-items: center; justify-content: center;
		flex-shrink: 0;
	}
	.file-details { flex: 1; text-align: left; display: flex; flex-direction: column; gap: 0.125rem; }
	.file-name { font-size: 0.875rem; font-weight: 600; color: var(--color-text); word-break: break-all; }
	.file-size { font-size: 0.75rem; color: var(--color-text-muted); }
	.remove-btn {
		background: none; border: none; color: var(--color-text-muted); cursor: pointer;
		padding: 0.5rem; border-radius: var(--radius-sm); display: flex;
		transition: color 0.15s, background 0.15s;
	}
	.remove-btn:hover { color: var(--color-danger); background: var(--color-danger-light); }

	/* Actions */
	.action-row { display: flex; gap: 0.75rem; }
	.analyze-btn {
		flex: 1;
		padding: 0.875rem;
		background: linear-gradient(135deg, var(--color-primary), #4f46e5);
		color: white;
		border: none;
		border-radius: var(--radius-md);
		font-size: 1rem;
		font-weight: 600;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s;
		box-shadow: 0 4px 14px color-mix(in srgb, var(--color-primary) 35%, transparent);
	}
	.analyze-btn:hover:not(:disabled) {
		transform: translateY(-1px);
		box-shadow: 0 6px 20px color-mix(in srgb, var(--color-primary) 45%, transparent);
	}
	.analyze-btn:active:not(:disabled) { transform: translateY(0); }
	.analyze-btn:disabled { opacity: 0.45; cursor: not-allowed; transform: none; box-shadow: none; }

	.export-btn {
		display: flex; align-items: center; gap: 0.375rem; padding: 0.875rem 1.25rem;
		background: color-mix(in srgb, var(--color-surface) 80%, transparent);
		backdrop-filter: blur(8px);
		color: var(--color-text); border: 1px solid var(--color-border);
		border-radius: var(--radius-md); font-size: 0.875rem; font-weight: 600;
		cursor: pointer; transition: background 0.15s, border-color 0.15s;
	}
	.export-btn:hover:not(:disabled) { background: var(--color-surface-hover); border-color: var(--color-text-muted); }
	.export-btn:disabled { opacity: 0.45; cursor: not-allowed; }

	.spinner { width: 18px; height: 18px; border: 2.5px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }

	/* Error */
	.error-banner {
		display: flex; align-items: flex-start; gap: 0.5rem; padding: 0.875rem 1rem;
		background: var(--color-danger-light); color: var(--color-danger);
		border-radius: var(--radius-md); font-size: 0.875rem; font-weight: 500;
		border: 1px solid color-mix(in srgb, var(--color-danger) 20%, transparent);
	}

	/* Results */
	.results { display: flex; flex-direction: column; gap: 1.25rem; }
	.result-card {
		animation: fadeUp 0.4s ease forwards;
	}
	.result-summary { border-left: 4px solid var(--color-primary); }

	.detected-role-badge {
		display: inline-flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.3125rem 0.75rem;
		border-radius: var(--radius-full);
		font-size: 0.8125rem;
		font-weight: 600;
		color: var(--color-primary);
		background: color-mix(in srgb, var(--color-primary) 10%, transparent);
		border: 1px solid color-mix(in srgb, var(--color-primary) 20%, transparent);
		margin-bottom: 0.75rem;
	}
	.summary-text { font-size: 0.9375rem; color: var(--color-text-secondary); line-height: 1.7; }

	/* Score cards with rings */
	.score-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; }
	.score-card {
		background: color-mix(in srgb, var(--color-surface) 85%, transparent);
		backdrop-filter: blur(12px);
		border-radius: var(--radius-lg);
		padding: 1.75rem 1.5rem;
		box-shadow: var(--shadow-md);
		border: 1px solid color-mix(in srgb, var(--color-border) 60%, transparent);
		text-align: center;
		transition: transform 0.2s, border-color 0.2s;
	}
	.score-card:hover {
		transform: translateY(-2px);
		border-color: var(--accent);
	}

	.score-ring-wrap {
		position: relative;
		width: 90px;
		height: 90px;
		margin: 0 auto 0.75rem;
	}
	.score-ring {
		width: 90px;
		height: 90px;
		transform: rotate(-90deg);
	}
	.ring-bg {
		stroke: var(--color-gray-100);
	}
	.ring-fill {
		stroke-linecap: round;
		transition: stroke-dasharray 1s ease;
	}
	.score-value {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		font-size: 1.5rem;
		font-weight: 800;
	}

	.score-card h3 { font-size: 0.875rem; font-weight: 700; color: var(--color-text); margin-bottom: 0.125rem; }
	.score-badge { font-size: 0.6875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
	.score-explanation { font-size: 0.8125rem; color: var(--color-text-secondary); line-height: 1.5; margin-top: 0.5rem; }

	/* Score header with pill */
	.score-header-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.75rem;
	}
	.score-pill {
		font-size: 0.8125rem;
		font-weight: 700;
		padding: 0.25rem 0.75rem;
		border-radius: var(--radius-full);
	}

	/* Sub Scores */
	.sub-scores { display: flex; flex-direction: column; gap: 0.875rem; }
	.sub-score-item { margin-bottom: 0.125rem; }
	.sub-score-header { display: flex; justify-content: space-between; margin-bottom: 0.375rem; font-size: 0.875rem; font-weight: 500; color: var(--color-text); }
	.sub-label { display: flex; align-items: center; gap: 0.375rem; }
	.sub-score-val { font-weight: 700; font-size: 0.8125rem; }
	.progress-bar { height: 8px; background: var(--color-gray-100); border-radius: var(--radius-full); overflow: hidden; }
	.progress-fill { height: 100%; border-radius: var(--radius-full); transition: width 0.8s ease; }

	/* Keywords / Tags */
	.keyword-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; }
	.tags { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }
	.tag { padding: 0.3125rem 0.75rem; border-radius: var(--radius-full); font-size: 0.8125rem; font-weight: 500; transition: transform 0.15s; }
	.tag:hover { transform: translateY(-1px); }
	.tag-matched { background: var(--color-success-light); color: var(--color-success); border: 1px solid color-mix(in srgb, var(--color-success) 20%, transparent); }
	.tag-missing { background: var(--color-danger-light); color: var(--color-danger); border: 1px solid color-mix(in srgb, var(--color-danger) 20%, transparent); }
	.empty-text { font-size: 0.8125rem; color: var(--color-text-muted); margin-top: 0.5rem; }

	/* Lists */
	.suggestion-list, .weak-list, .tip-list { list-style: none; margin-top: 0.5rem; display: flex; flex-direction: column; gap: 0.5rem; }
	.suggestion-list li, .weak-list li, .tip-list li {
		display: flex;
		align-items: flex-start;
		gap: 0.625rem;
		padding: 0.75rem 1rem;
		border-radius: var(--radius-md);
		font-size: 0.875rem;
		line-height: 1.5;
		transition: transform 0.15s;
	}
	.suggestion-list li:hover, .weak-list li:hover, .tip-list li:hover { transform: translateX(2px); }
	.suggestion-list li svg, .weak-list li svg, .tip-list li svg { flex-shrink: 0; margin-top: 0.125rem; }
	.suggestion-list li { background: color-mix(in srgb, var(--color-primary) 6%, transparent); color: var(--color-text-secondary); border: 1px solid color-mix(in srgb, var(--color-primary) 12%, transparent); }
	.weak-list li { background: color-mix(in srgb, var(--color-warning) 6%, transparent); color: var(--color-text-secondary); border: 1px solid color-mix(in srgb, var(--color-warning) 12%, transparent); }
	.tip-list li { background: color-mix(in srgb, #10b981 6%, transparent); color: var(--color-text-secondary); border: 1px solid color-mix(in srgb, #10b981 12%, transparent); }

	/* Question list */
	.question-list {
		list-style: none;
		margin-top: 0.5rem;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
	.question-list li {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
		padding: 0.75rem 1rem;
		border-radius: var(--radius-md);
		font-size: 0.875rem;
		line-height: 1.5;
		background: color-mix(in srgb, var(--accent, var(--color-primary)) 5%, transparent);
		border: 1px solid color-mix(in srgb, var(--accent, var(--color-primary)) 10%, transparent);
		color: var(--color-text-secondary);
		transition: transform 0.15s;
	}
	.question-list li:hover { transform: translateX(2px); }
	.q-num {
		flex-shrink: 0;
		width: 22px;
		height: 22px;
		border-radius: 50%;
		background: color-mix(in srgb, var(--accent, var(--color-primary)) 15%, transparent);
		color: var(--accent, var(--color-primary));
		font-size: 0.6875rem;
		font-weight: 700;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-top: 0.0625rem;
	}

	/* Cover letter */
	.cover-letter-text {
		white-space: pre-wrap;
		font-family: inherit;
		font-size: 0.875rem;
		line-height: 1.7;
		color: var(--color-text-secondary);
		background: color-mix(in srgb, var(--color-bg) 60%, transparent);
		padding: 1.25rem;
		border-radius: var(--radius-md);
		border: 1px solid var(--color-border);
		margin-bottom: 0.75rem;
	}
	.copy-btn {
		display: inline-flex;
		align-items: center;
		gap: 0.375rem;
		padding: 0.5rem 1rem;
		background: linear-gradient(135deg, var(--color-primary), #4f46e5);
		color: white;
		border: none;
		border-radius: var(--radius-sm);
		font-size: 0.8125rem;
		font-weight: 600;
		cursor: pointer;
		transition: transform 0.15s, box-shadow 0.15s;
		box-shadow: 0 2px 8px color-mix(in srgb, var(--color-primary) 30%, transparent);
	}
	.copy-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px color-mix(in srgb, var(--color-primary) 40%, transparent); }

	/* Skill gap */
	.improve-item {
		padding: 0.875rem;
		background: color-mix(in srgb, var(--color-bg) 60%, transparent);
		border-radius: var(--radius-md);
		margin-bottom: 0.5rem;
		border: 1px solid var(--color-border);
		transition: transform 0.15s;
	}
	.improve-item:hover { transform: translateX(2px); }
	.improve-item strong { font-size: 0.875rem; color: var(--color-text); }
	.improve-item p { font-size: 0.8125rem; color: var(--color-text-secondary); margin-top: 0.25rem; }

	.roadmap-grid { display: flex; flex-direction: column; gap: 0.75rem; margin-top: 0.5rem; }
	.roadmap-item {
		padding: 1rem;
		background: color-mix(in srgb, var(--color-bg) 60%, transparent);
		border-radius: var(--radius-md);
		border: 1px solid var(--color-border);
		transition: transform 0.15s, border-color 0.15s;
	}
	.roadmap-item:hover { transform: translateX(2px); border-color: var(--color-text-muted); }
	.roadmap-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.375rem; }
	.roadmap-header strong { font-size: 0.875rem; color: var(--color-text); }
	.priority-badge { font-size: 0.6875rem; font-weight: 700; text-transform: uppercase; padding: 0.1875rem 0.5rem; border-radius: var(--radius-full); }
	.priority-high { background: var(--color-danger-light); color: var(--color-danger); }
	.priority-medium { background: var(--color-warning-light); color: var(--color-warning); }
	.priority-low { background: var(--color-success-light); color: var(--color-success); }
	.roadmap-resource { font-size: 0.8125rem; color: var(--color-text-secondary); }
	.roadmap-time { font-size: 0.75rem; color: var(--color-text-muted); margin-top: 0.25rem; }

	/* Reset */
	.reset-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		width: 100%;
		padding: 0.875rem;
		background: color-mix(in srgb, var(--color-surface) 80%, transparent);
		backdrop-filter: blur(8px);
		color: var(--color-text-secondary);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		font-size: 0.875rem;
		font-weight: 600;
		cursor: pointer;
		transition: background 0.15s, color 0.15s, border-color 0.15s;
	}
	.reset-btn:hover { background: var(--color-surface-hover); color: var(--color-text); border-color: var(--color-text-muted); }

	@media (max-width: 768px) {
		.container { padding: 1rem 1rem 3rem; }
		.page-header h1 { font-size: 1.5rem; }
		.score-grid, .keyword-grid { grid-template-columns: 1fr; }
		.tabs { gap: 0.25rem; }
		.tab { padding: 0.375rem 0.75rem; font-size: 0.75rem; }
		.tab svg { display: none; }
	}

	@media (max-width: 480px) {
		.page-header h1 { font-size: 1.375rem; }
		.page-subtitle { font-size: 0.8125rem; }
		.card { padding: 1.25rem; }
		.score-card { padding: 1.25rem 1rem; }
		.action-row { flex-direction: column; }
	}
</style>
