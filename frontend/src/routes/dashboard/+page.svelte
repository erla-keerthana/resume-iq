<script lang="ts">
	import { base } from '$app/paths';
	import { auth } from '$lib/stores.svelte';
	import { getHistory, deleteHistoryEntry, getHistoryDetail } from '$lib/api';
	import type { HistoryEntry, AnalysisResult } from '$lib/types';
	let entries = $state<HistoryEntry[]>([]);
	let loading = $state(true);
	let error = $state('');
	let selectedResult = $state<AnalysisResult | null>(null);
	let selectedFilename = $state('');
	let mounted = $state(false);
	let deletingId = $state<string | null>(null);
	let historyLoaded = false;

	$effect(() => {
		if (!auth.ready) return;
		mounted = true;
		if (auth.isLoggedIn && !historyLoaded) {
			historyLoaded = true;
			loadHistory();
		}
		if (!auth.isLoggedIn) {
			loading = false;
		}
	});

	async function loadHistory() {
		loading = true;
		error = '';
		try {
			entries = await getHistory();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load history.';
		} finally {
			loading = false;
		}
	}

	async function handleDelete(id: string) {
		deletingId = id;
		try {
			await deleteHistoryEntry(id);
			entries = entries.filter(e => e.id !== id);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Delete failed.';
		} finally {
			deletingId = null;
		}
	}

	async function handleView(entry: HistoryEntry) {
		try {
			const detail = await getHistoryDetail(entry.id);
			selectedResult = detail.result_json;
			selectedFilename = entry.filename;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load details.';
		}
	}

	function closeModal() {
		selectedResult = null;
		selectedFilename = '';
	}

	function scoreColor(score: number): string {
		if (score >= 80) return '#22c55e';
		if (score >= 60) return '#f59e0b';
		return '#ef4444';
	}

	function scoreBg(score: number): string {
		if (score >= 80) return 'var(--color-success-light)';
		if (score >= 60) return 'var(--color-warning-light)';
		return 'var(--color-danger-light)';
	}

	function formatDate(iso: string): string {
		try { return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' }); }
		catch { return iso; }
	}

	let avgAts = $derived(entries.length ? Math.round(entries.reduce((a, e) => a + e.ats_score, 0) / entries.length) : 0);
	let avgMatch = $derived(entries.length ? Math.round(entries.reduce((a, e) => a + e.match_score, 0) / entries.length) : 0);
	let bestAts = $derived(entries.length ? Math.max(...entries.map(e => e.ats_score)) : 0);
</script>

<svelte:head>
	<title>Dashboard - ResumeIQ</title>
</svelte:head>

<div class="page" class:mounted>
	<main class="container">
		<!-- Header -->
		<div class="page-header anim-fade-up" style="--delay: 0s">
			<div class="header-text">
				<span class="section-tag">Dashboard</span>
				<h1>Your <span class="gradient-text">Analysis History</span></h1>
				<p class="subtitle">Track your resume improvements and review past analyses.</p>
			</div>
			{#if auth.isLoggedIn && entries.length > 0}
				<a href="{base}/analyze" class="header-action">
					<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
					New Analysis
				</a>
			{/if}
		</div>

		{#if !auth.isLoggedIn}
			<!-- Not logged in -->
			<div class="empty-card anim-fade-up" style="--delay: 0.1s">
				<div class="empty-icon-wrap">
					<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
						<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
					</svg>
				</div>
				<h2 class="empty-title">Login Required</h2>
				<p class="empty-desc">Sign in to view your analysis history and track your progress over time.</p>
				<div class="empty-actions">
					<a href="{base}/login" class="btn-primary">Sign In</a>
					<a href="{base}/signup" class="btn-secondary">Create Account</a>
				</div>
			</div>
		{:else if loading}
			<!-- Loading -->
			<div class="loading-state anim-fade-up" style="--delay: 0.1s">
				<span class="spinner-lg"></span>
				<p>Loading your history...</p>
			</div>
		{:else if error}
			<!-- Error -->
			<div class="error-banner anim-fade-up" style="--delay: 0.1s" role="alert">
				<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
				<span>{error}</span>
				<button class="error-retry" onclick={loadHistory}>Retry</button>
			</div>
		{:else if entries.length === 0}
			<!-- Empty state -->
			<div class="empty-card anim-fade-up" style="--delay: 0.1s">
				<div class="empty-icon-wrap">
					<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
						<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/>
					</svg>
				</div>
				<h2 class="empty-title">No Analyses Yet</h2>
				<p class="empty-desc">Your resume analysis results will appear here. Start by analyzing your first resume.</p>
				<div class="empty-actions">
					<a href="{base}/analyze" class="btn-primary">
						<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/></svg>
						Analyze a Resume
					</a>
				</div>
			</div>
		{:else}
			<!-- Stats -->
			<div class="stats-row">
				{#each [
					{ icon: 'layers', value: entries.length.toString(), label: 'Total Analyses', color: '#3b82f6' },
					{ icon: 'bar', value: avgAts.toString(), label: 'Avg ATS Score', color: scoreColor(avgAts) },
					{ icon: 'match', value: avgMatch.toString(), label: 'Avg Match Score', color: scoreColor(avgMatch) },
					{ icon: 'trophy', value: bestAts.toString(), label: 'Best ATS Score', color: scoreColor(bestAts) }
				] as s, i}
					<div class="stat-card anim-fade-up" style="--delay: {0.05 * i}s; --accent: {s.color}">
						<div class="stat-icon-wrap" style="--accent: {s.color}">
							{#if s.icon === 'layers'}
								<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{s.color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
							{:else if s.icon === 'bar'}
								<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{s.color}" stroke-width="2" stroke-linecap="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
							{:else if s.icon === 'match'}
								<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{s.color}" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
							{:else}
								<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{s.color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5C6 4 6 7 12 7s6-3 7.5-3a2.5 2.5 0 0 1 0 5H18"/><path d="M5 21V11h14v10"/><path d="M9 21v-4h6v4"/></svg>
							{/if}
						</div>
						<span class="stat-value" style="color: {s.color}">{s.value}</span>
						<span class="stat-label">{s.label}</span>
					</div>
				{/each}
			</div>

			<!-- History list -->
			<div class="history-section anim-fade-up" style="--delay: 0.2s">
				<h2 class="history-heading">Recent Analyses</h2>
				<div class="history-list">
					{#each entries as entry, i}
						<div class="history-item anim-fade-up" style="--delay: {0.05 * i + 0.25}s">
							<div class="history-icon">
								<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-text-muted)" stroke-width="1.5" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
							</div>
							<div class="history-info">
								<span class="history-filename">{entry.filename}</span>
								<span class="history-meta">
									<span class="history-date">{formatDate(entry.created_at)}</span>
									<span class="history-jd">{entry.job_description}</span>
								</span>
							</div>
							<div class="history-scores">
								<div class="score-badge" style="background: {scoreBg(entry.ats_score)}; color: {scoreColor(entry.ats_score)}">
									ATS {entry.ats_score}
								</div>
								<div class="score-badge" style="background: {scoreBg(entry.match_score)}; color: {scoreColor(entry.match_score)}">
									Match {entry.match_score}
								</div>
							</div>
							<div class="history-actions">
								<button class="action-btn view-btn" onclick={() => handleView(entry)} title="View details">
									<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
								</button>
								<button class="action-btn delete-btn" onclick={() => handleDelete(entry.id)} disabled={deletingId === entry.id} title="Delete">
									{#if deletingId === entry.id}
										<span class="spinner-sm"></span>
									{:else}
										<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
									{/if}
								</button>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Detail Modal -->
		{#if selectedResult}
			<!-- svelte-ignore a11y_interactive_supports_focus -->
			<!-- svelte-ignore a11y_no_static_element_interactions -->
			<!-- svelte-ignore a11y_click_events_have_key_events -->
			<div class="modal-overlay" role="dialog" aria-label="Analysis detail" tabindex="-1" onclick={closeModal} onkeydown={(e: KeyboardEvent) => { if (e.key === 'Escape') closeModal(); }}>
				<div class="modal-content" onclick={(e: MouseEvent) => e.stopPropagation()}>
					<div class="modal-header">
						<div>
							<h2>{selectedFilename}</h2>
							<span class="modal-role">{selectedResult.detected_role}</span>
						</div>
						<button class="modal-close" onclick={closeModal} aria-label="Close">
							<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
						</button>
					</div>
					<div class="modal-body">
						<p class="summary-text">{selectedResult.summary}</p>

						<!-- Score grid -->
						<div class="modal-scores">
							{#each [
								{ label: 'ATS Score', v: selectedResult.ats_score },
								{ label: 'Match Score', v: selectedResult.match_score },
								{ label: 'Skills', v: selectedResult.skills_score },
								{ label: 'Keywords', v: selectedResult.keyword_score },
								{ label: 'Experience', v: selectedResult.experience_score },
								{ label: 'Projects', v: selectedResult.project_score },
							] as s}
								<div class="modal-score-item">
									<span class="modal-score-label">{s.label}</span>
									<div class="modal-score-bar-wrap">
										<div class="modal-score-bar" style="width: {s.v}%; background: {scoreColor(s.v)}"></div>
									</div>
									<span class="modal-score-val" style="color: {scoreColor(s.v)}">{s.v}</span>
								</div>
							{/each}
						</div>

						<!-- Keywords -->
						{#if selectedResult.matched_keywords?.length || selectedResult.missing_keywords?.length}
							<div class="modal-section">
								<h3>Keywords</h3>
								<div class="modal-tags">
									{#each selectedResult.matched_keywords as k}
										<span class="modal-tag tag-green">{k}</span>
									{/each}
									{#each selectedResult.missing_keywords as k}
										<span class="modal-tag tag-red">{k}</span>
									{/each}
								</div>
							</div>
						{/if}

						<!-- Suggestions -->
						{#if selectedResult.suggestions?.length}
							<div class="modal-section">
								<h3>Suggestions</h3>
								<ul class="modal-list">
									{#each selectedResult.suggestions as s}
										<li>{s}</li>
									{/each}
								</ul>
							</div>
						{/if}

						<!-- Weak points -->
						{#if selectedResult.weak_points?.length}
							<div class="modal-section">
								<h3>Areas to Improve</h3>
								<ul class="modal-list list-warn">
									{#each selectedResult.weak_points as w}
										<li>{w}</li>
									{/each}
								</ul>
							</div>
						{/if}
					</div>
				</div>
			</div>
		{/if}
	</main>
</div>

<style>
	/* ================================================================
	   ANIMATIONS
	   ================================================================ */
	@keyframes fadeUp {
		from { opacity: 0; transform: translateY(20px); }
		to { opacity: 1; transform: translateY(0); }
	}
	@keyframes spin { to { transform: rotate(360deg); } }

	.anim-fade-up { opacity: 0; transform: translateY(20px); }
	.mounted .anim-fade-up {
		animation: fadeUp 0.5s ease-out forwards;
		animation-delay: var(--delay, 0s);
	}

	/* ================================================================
	   LAYOUT
	   ================================================================ */
	.page { min-height: 100vh; background: var(--color-bg); }
	.container { max-width: 920px; margin: 0 auto; padding: 2.5rem 2rem 4rem; }

	/* ================================================================
	   HEADER
	   ================================================================ */
	.page-header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		margin-bottom: 2rem;
		gap: 1rem;
	}
	.section-tag {
		display: inline-block;
		padding: 0.3rem 0.875rem;
		background: color-mix(in srgb, var(--color-primary) 10%, transparent);
		color: var(--color-primary);
		border-radius: 9999px;
		font-size: 0.75rem;
		font-weight: 600;
		letter-spacing: 0.03em;
		margin-bottom: 0.625rem;
		border: 1px solid color-mix(in srgb, var(--color-primary) 15%, transparent);
	}
	.page-header h1 {
		font-size: 2rem;
		font-weight: 800;
		color: var(--color-text);
		letter-spacing: -0.03em;
		line-height: 1.2;
	}
	.gradient-text {
		background: linear-gradient(135deg, var(--color-primary), #8b5cf6, #06b6d4);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}
	.subtitle { font-size: 0.9375rem; color: var(--color-text-muted); margin-top: 0.375rem; }

	.header-action {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.625rem 1.25rem;
		background: var(--color-primary);
		color: white;
		font-size: 0.875rem;
		font-weight: 600;
		border-radius: 9999px;
		text-decoration: none;
		transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
		white-space: nowrap;
		margin-top: 0.5rem;
	}
	.header-action:hover {
		background: var(--color-primary-hover);
		transform: translateY(-1px);
		box-shadow: 0 4px 12px color-mix(in srgb, var(--color-primary) 30%, transparent);
		text-decoration: none;
	}

	/* ================================================================
	   EMPTY / LOADING / ERROR STATES
	   ================================================================ */
	.empty-card {
		text-align: center;
		padding: 4rem 2rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 16px;
		box-shadow: var(--shadow-md);
	}
	.empty-icon-wrap {
		width: 80px;
		height: 80px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 20px;
		background: color-mix(in srgb, var(--color-primary) 8%, transparent);
		margin: 0 auto 1.5rem;
	}
	.empty-title { font-size: 1.375rem; font-weight: 700; color: var(--color-text); margin-bottom: 0.5rem; }
	.empty-desc { font-size: 0.9375rem; color: var(--color-text-secondary); max-width: 380px; margin: 0 auto 2rem; line-height: 1.6; }
	.empty-actions { display: flex; justify-content: center; gap: 0.75rem; flex-wrap: wrap; }

	.btn-primary {
		display: inline-flex; align-items: center; gap: 0.5rem;
		padding: 0.75rem 1.75rem; background: var(--color-primary); color: white;
		font-size: 0.9375rem; font-weight: 600; border-radius: 9999px;
		text-decoration: none; transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
	}
	.btn-primary:hover { background: var(--color-primary-hover); transform: translateY(-1px); box-shadow: 0 6px 16px color-mix(in srgb, var(--color-primary) 30%, transparent); text-decoration: none; }

	.btn-secondary {
		display: inline-flex; align-items: center;
		padding: 0.75rem 1.75rem; background: var(--color-surface); color: var(--color-text);
		font-size: 0.9375rem; font-weight: 600; border: 1px solid var(--color-border); border-radius: 9999px;
		text-decoration: none; transition: background 0.2s, border-color 0.2s;
	}
	.btn-secondary:hover { background: var(--color-surface-hover); border-color: var(--color-text-muted); text-decoration: none; }

	.loading-state {
		text-align: center; padding: 5rem 2rem; color: var(--color-text-muted);
	}
	.spinner-lg {
		display: inline-block; width: 36px; height: 36px;
		border: 3px solid var(--color-border); border-top-color: var(--color-primary);
		border-radius: 50%; animation: spin 0.7s linear infinite; margin-bottom: 1rem;
	}
	.spinner-sm {
		display: inline-block; width: 14px; height: 14px;
		border: 2px solid var(--color-border); border-top-color: var(--color-danger);
		border-radius: 50%; animation: spin 0.7s linear infinite;
	}

	.error-banner {
		display: flex; align-items: center; gap: 0.625rem;
		padding: 0.875rem 1.25rem; background: var(--color-danger-light);
		color: var(--color-danger); border-radius: 12px; font-size: 0.875rem;
		border: 1px solid color-mix(in srgb, var(--color-danger) 20%, transparent);
	}
	.error-retry {
		margin-left: auto; padding: 0.375rem 1rem; background: var(--color-danger);
		color: white; border: none; border-radius: 9999px; font-size: 0.8125rem;
		font-weight: 600; cursor: pointer; font-family: inherit;
		transition: opacity 0.15s;
	}
	.error-retry:hover { opacity: 0.85; }

	/* ================================================================
	   STATS
	   ================================================================ */
	.stats-row {
		display: grid; grid-template-columns: repeat(4, 1fr);
		gap: 1rem; margin-bottom: 2rem;
	}
	.stat-card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 14px;
		padding: 1.25rem;
		text-align: center;
		transition: transform 0.25s, box-shadow 0.25s, border-color 0.25s;
		position: relative;
		overflow: hidden;
	}
	.stat-card::before {
		content: '';
		position: absolute; top: 0; left: 0; right: 0; height: 3px;
		background: var(--accent);
		opacity: 0; transition: opacity 0.25s;
	}
	.stat-card:hover {
		transform: translateY(-3px);
		box-shadow: 0 8px 24px -8px color-mix(in srgb, var(--accent) 15%, transparent), var(--shadow-md);
		border-color: color-mix(in srgb, var(--accent) 25%, var(--color-border));
	}
	.stat-card:hover::before { opacity: 1; }

	.stat-icon-wrap {
		width: 40px; height: 40px;
		display: flex; align-items: center; justify-content: center;
		border-radius: 10px;
		background: color-mix(in srgb, var(--accent) 10%, transparent);
		margin: 0 auto 0.75rem;
		transition: transform 0.25s;
	}
	.stat-card:hover .stat-icon-wrap { transform: scale(1.1); }

	.stat-value { display: block; font-size: 1.75rem; font-weight: 800; letter-spacing: -0.02em; }
	.stat-label { display: block; font-size: 0.75rem; color: var(--color-text-muted); font-weight: 500; margin-top: 0.125rem; }

	/* ================================================================
	   HISTORY
	   ================================================================ */
	.history-section {}
	.history-heading {
		font-size: 1.0625rem; font-weight: 700; color: var(--color-text);
		margin-bottom: 1rem;
	}
	.history-list { display: flex; flex-direction: column; gap: 0.625rem; }

	.history-item {
		display: flex; align-items: center; gap: 1rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 12px;
		padding: 1rem 1.25rem;
		transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
	}
	.history-item:hover {
		transform: translateY(-2px);
		box-shadow: var(--shadow-md);
		border-color: color-mix(in srgb, var(--color-primary) 20%, var(--color-border));
	}

	.history-icon {
		width: 40px; height: 40px;
		display: flex; align-items: center; justify-content: center;
		border-radius: 10px;
		background: var(--color-bg);
		flex-shrink: 0;
	}

	.history-info { flex: 1; min-width: 0; }
	.history-filename {
		display: block; font-weight: 600; font-size: 0.9375rem;
		color: var(--color-text); white-space: nowrap;
		overflow: hidden; text-overflow: ellipsis;
	}
	.history-meta {
		display: flex; gap: 0.75rem; align-items: center;
		margin-top: 0.25rem;
	}
	.history-date { font-size: 0.75rem; color: var(--color-text-muted); white-space: nowrap; }
	.history-jd {
		font-size: 0.75rem; color: var(--color-text-secondary);
		white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
		max-width: 220px;
	}

	.history-scores { display: flex; gap: 0.5rem; flex-shrink: 0; }
	.score-badge {
		padding: 0.3rem 0.75rem;
		border-radius: 9999px;
		font-size: 0.75rem;
		font-weight: 700;
		white-space: nowrap;
	}

	.history-actions { display: flex; gap: 0.375rem; flex-shrink: 0; }
	.action-btn {
		width: 36px; height: 36px;
		display: flex; align-items: center; justify-content: center;
		border: 1px solid var(--color-border);
		border-radius: 10px; cursor: pointer;
		background: var(--color-surface);
		color: var(--color-text-muted);
		transition: all 0.2s;
	}
	.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
	.view-btn:hover { background: color-mix(in srgb, var(--color-primary) 10%, transparent); color: var(--color-primary); border-color: var(--color-primary); }
	.delete-btn:hover:not(:disabled) { background: var(--color-danger-light); color: var(--color-danger); border-color: var(--color-danger); }

	/* ================================================================
	   MODAL
	   ================================================================ */
	.modal-overlay {
		position: fixed; inset: 0;
		background: rgba(0,0,0,0.5);
		backdrop-filter: blur(4px);
		z-index: 1000;
		display: flex; align-items: center; justify-content: center;
		padding: 2rem;
	}
	.modal-content {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 16px;
		max-width: 640px;
		width: 100%;
		max-height: 85vh;
		overflow-y: auto;
		box-shadow: 0 24px 48px -12px rgba(0,0,0,0.25);
		animation: fadeUp 0.3s ease-out;
	}
	.modal-header {
		display: flex; justify-content: space-between; align-items: flex-start;
		padding: 1.5rem 1.5rem 1rem;
		border-bottom: 1px solid var(--color-border);
	}
	.modal-header h2 { font-size: 1.125rem; font-weight: 700; color: var(--color-text); }
	.modal-role { font-size: 0.8125rem; color: var(--color-primary); font-weight: 500; margin-top: 0.125rem; display: block; }
	.modal-close {
		background: var(--color-bg); border: 1px solid var(--color-border);
		color: var(--color-text-muted); cursor: pointer; padding: 0.375rem;
		border-radius: 8px; transition: all 0.15s;
		display: flex; align-items: center; justify-content: center;
	}
	.modal-close:hover { background: var(--color-surface-hover); color: var(--color-text); }

	.modal-body { padding: 1.5rem; }
	.summary-text { font-size: 0.9375rem; color: var(--color-text-secondary); line-height: 1.65; margin-bottom: 1.5rem; }

	.modal-scores { display: flex; flex-direction: column; gap: 0.625rem; margin-bottom: 1.5rem; }
	.modal-score-item {
		display: flex; align-items: center; gap: 0.75rem;
	}
	.modal-score-label { font-size: 0.8125rem; color: var(--color-text-secondary); width: 80px; font-weight: 500; }
	.modal-score-bar-wrap {
		flex: 1; height: 8px; background: var(--color-bg);
		border-radius: 4px; overflow: hidden;
	}
	.modal-score-bar {
		height: 100%; border-radius: 4px;
		transition: width 0.6s ease-out;
	}
	.modal-score-val { font-size: 0.875rem; font-weight: 700; width: 28px; text-align: right; }

	.modal-section { margin-bottom: 1.25rem; }
	.modal-section h3 {
		font-size: 0.875rem; font-weight: 700; color: var(--color-text);
		margin-bottom: 0.625rem;
	}
	.modal-tags { display: flex; flex-wrap: wrap; gap: 0.375rem; }
	.modal-tag {
		padding: 0.25rem 0.75rem; border-radius: 9999px;
		font-size: 0.75rem; font-weight: 600;
	}
	.tag-green { background: var(--color-success-light); color: var(--color-success); }
	.tag-red { background: var(--color-danger-light); color: var(--color-danger); }

	.modal-list {
		padding-left: 0; list-style: none;
		font-size: 0.8125rem; color: var(--color-text-secondary); line-height: 1.7;
	}
	.modal-list li {
		padding: 0.375rem 0 0.375rem 1.5rem;
		position: relative;
	}
	.modal-list li::before {
		content: '';
		position: absolute; left: 0; top: 0.75rem;
		width: 6px; height: 6px; border-radius: 50%;
		background: var(--color-primary);
	}
	.list-warn li::before { background: var(--color-warning); }

	/* ================================================================
	   RESPONSIVE
	   ================================================================ */
	@media (max-width: 768px) {
		.container { padding: 1.5rem 1.25rem 3rem; }
		.page-header { flex-direction: column; }
		.page-header h1 { font-size: 1.5rem; }
		.stats-row { grid-template-columns: repeat(2, 1fr); }
		.history-item { flex-wrap: wrap; }
		.history-icon { display: none; }
		.history-scores { order: 3; width: 100%; }
		.history-actions { order: 4; margin-left: auto; }
		.modal-content { max-height: 90vh; }
	}
	@media (max-width: 480px) {
		.stats-row { grid-template-columns: 1fr 1fr; gap: 0.75rem; }
		.history-meta { flex-direction: column; gap: 0.125rem; }
		.empty-card { padding: 3rem 1.5rem; }
	}
</style>
