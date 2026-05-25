<script lang="ts">
	import { base } from '$app/paths';
	import { auth, theme } from '$lib/stores.svelte';
	import { onMount } from 'svelte';

	let mounted = $state(false);
	onMount(() => {
		theme.init();
		requestAnimationFrame(() => { mounted = true; });
	});

	const features = [
		{
			icon: 'upload',
			title: 'Multi-Format Upload',
			desc: 'Drag & drop PDF, DOCX, TXT, JPG, or PNG files for instant processing.',
			color: '#3b82f6'
		},
		{
			icon: 'chart',
			title: 'ATS Score Analysis',
			desc: 'Get detailed ATS compatibility scores with actionable explanations.',
			color: '#8b5cf6'
		},
		{
			icon: 'target',
			title: 'Skill Gap Analysis',
			desc: 'Identify missing skills and get a personalized learning roadmap.',
			color: '#06b6d4'
		},
		{
			icon: 'key',
			title: 'Keyword Optimizer',
			desc: 'Optimize your resume keywords to pass through ATS filters.',
			color: '#f59e0b'
		},
		{
			icon: 'letter',
			title: 'Cover Letter Generator',
			desc: 'Generate tailored cover letters matched to specific job postings.',
			color: '#10b981'
		},
		{
			icon: 'chat',
			title: 'Interview Prep',
			desc: 'Get custom interview questions and expert tips for your role.',
			color: '#ec4899'
		},
		{
			icon: 'pdf',
			title: 'Export PDF Reports',
			desc: 'Download professional analysis reports to track your progress.',
			color: '#ef4444'
		},
		{
			icon: 'link',
			title: 'LinkedIn & GitHub',
			desc: 'Parse your online profiles for instant resume-level analysis.',
			color: '#6366f1'
		}
	];

	const steps = [
		{ num: '01', title: 'Upload Resume', desc: 'Drop your resume in any format' },
		{ num: '02', title: 'Add Job Description', desc: 'Paste the target job posting' },
		{ num: '03', title: 'Get AI Analysis', desc: 'Receive detailed scores & insights' }
	];

	const stats = [
		{ value: '95%', label: 'ATS Accuracy' },
		{ value: '8+', label: 'File Formats' },
		{ value: '6', label: 'AI Tools' },
		{ value: '< 30s', label: 'Analysis Time' }
	];
</script>

<svelte:head>
	<title>ResumeIQ - AI Resume Analyzer</title>
</svelte:head>

<div class="landing" class:mounted>
	<!-- Navbar -->
	<nav class="nav">
		<div class="nav-inner">
			<a href="{base}/" class="nav-brand">
				<svg class="nav-brand-icon" width="28" height="28" viewBox="0 0 24 24" fill="none">
					<rect x="3" y="2" width="18" height="20" rx="3" stroke="currentColor" stroke-width="1.5"/>
					<path d="M7 7h10M7 11h7M7 15h5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
					<circle cx="17" cy="17" r="4" fill="var(--color-primary)" stroke="var(--color-primary)" stroke-width="1"/>
					<path d="M15.5 17l1 1 2-2" stroke="white" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
				</svg>
				Resume<span class="brand-iq">IQ</span>
			</a>
			<div class="nav-actions">
				<button class="theme-btn" onclick={() => theme.toggle()} aria-label="Toggle dark mode">
					{#if theme.dark}
						<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
					{:else}
						<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
					{/if}
				</button>
				{#if auth.isLoggedIn}
					<a href="{base}/analyze" class="nav-link">Analyze</a>
					<a href="{base}/dashboard" class="nav-link">Dashboard</a>
					<button class="nav-link" onclick={() => auth.logout()}>Logout</button>
				{:else}
					<a href="{base}/login" class="nav-link">Login</a>
					<a href="{base}/signup" class="nav-btn-primary">Sign Up</a>
				{/if}
			</div>
		</div>
	</nav>

	<!-- Hero -->
	<section class="hero">
		<div class="hero-glow hero-glow-1"></div>
		<div class="hero-glow hero-glow-2"></div>
		<div class="hero-glow hero-glow-3"></div>

		<div class="hero-content anim-fade-up" style="--delay: 0s">
			<div class="badge anim-fade-up" style="--delay: 0.1s">
				<span class="badge-dot"></span>
				AI-Powered Resume Analysis
			</div>
			<h1 class="hero-title anim-fade-up" style="--delay: 0.2s">
				Land Your Dream Job<br/>
				With <span class="gradient-text">ResumeIQ</span>
			</h1>
			<p class="hero-subtitle anim-fade-up" style="--delay: 0.3s">
				Upload your resume, paste a job description, and get instant AI-powered feedback —
				ATS scoring, skill matching, keyword optimization, and actionable suggestions to
				make your resume stand out.
			</p>
			<div class="hero-ctas anim-fade-up" style="--delay: 0.4s">
				<a href="{base}/analyze" class="btn-primary">
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/></svg>
					Analyze Resume
					<span class="btn-arrow">&rarr;</span>
				</a>
				{#if auth.isLoggedIn}
					<a href="{base}/dashboard" class="btn-secondary">View Dashboard</a>
				{:else}
					<a href="{base}/signup" class="btn-secondary">Create Free Account</a>
				{/if}
			</div>
		</div>

		<!-- Floating mock UI card -->
		<div class="hero-visual anim-fade-up" style="--delay: 0.5s">
			<div class="mock-card">
				<div class="mock-header">
					<div class="mock-dots"><span></span><span></span><span></span></div>
					<span class="mock-title">resume_analysis.pdf</span>
				</div>
				<div class="mock-body">
					<div class="mock-score-row">
						<div class="mock-score">
							<svg class="mock-ring" viewBox="0 0 36 36">
								<path class="mock-ring-bg" d="M18 2.0845a 15.9155 15.9155 0 0 1 0 31.831a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke-width="3"/>
								<path class="mock-ring-fill" d="M18 2.0845a 15.9155 15.9155 0 0 1 0 31.831a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke-width="3" stroke-dasharray="87, 100"/>
							</svg>
							<span class="mock-score-val">87</span>
							<span class="mock-score-label">ATS Score</span>
						</div>
						<div class="mock-score">
							<svg class="mock-ring" viewBox="0 0 36 36">
								<path class="mock-ring-bg" d="M18 2.0845a 15.9155 15.9155 0 0 1 0 31.831a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke-width="3"/>
								<path class="mock-ring-fill ring-green" d="M18 2.0845a 15.9155 15.9155 0 0 1 0 31.831a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke-width="3" stroke-dasharray="92, 100"/>
							</svg>
							<span class="mock-score-val">92</span>
							<span class="mock-score-label">Match</span>
						</div>
					</div>
					<div class="mock-tags">
						<span class="mock-tag tag-green">React</span>
						<span class="mock-tag tag-green">TypeScript</span>
						<span class="mock-tag tag-green">Node.js</span>
						<span class="mock-tag tag-red">Kubernetes</span>
						<span class="mock-tag tag-red">AWS</span>
					</div>
					<div class="mock-bars">
						<div class="mock-bar"><span class="mock-bar-label">Skills</span><div class="mock-bar-track"><div class="mock-bar-fill" style="width:85%"></div></div></div>
						<div class="mock-bar"><span class="mock-bar-label">Keywords</span><div class="mock-bar-track"><div class="mock-bar-fill fill-purple" style="width:78%"></div></div></div>
						<div class="mock-bar"><span class="mock-bar-label">Experience</span><div class="mock-bar-track"><div class="mock-bar-fill fill-cyan" style="width:91%"></div></div></div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- Stats -->
	<section class="stats-section">
		<div class="stats-grid">
			{#each stats as s, i}
				<div class="stat-item anim-fade-up" style="--delay: {0.1 * i}s">
					<span class="stat-value">{s.value}</span>
					<span class="stat-label">{s.label}</span>
				</div>
			{/each}
		</div>
	</section>

	<!-- Features -->
	<section class="features-section">
		<div class="section-header anim-fade-up" style="--delay: 0s">
			<span class="section-tag">Features</span>
			<h2 class="section-title">Everything You Need to<br/><span class="gradient-text">Optimize Your Resume</span></h2>
			<p class="section-desc">Comprehensive AI-powered tools to analyze, improve, and perfect your resume for any role.</p>
		</div>
		<div class="features-grid">
			{#each features as f, i}
				<div class="feature-card anim-fade-up" style="--delay: {0.05 * i}s; --accent: {f.color}">
					<div class="feature-icon-wrap" style="--accent: {f.color}">
						{#if f.icon === 'upload'}
							<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{f.color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
						{:else if f.icon === 'chart'}
							<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{f.color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
						{:else if f.icon === 'target'}
							<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{f.color}" stroke-width="1.8"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
						{:else if f.icon === 'key'}
							<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{f.color}" stroke-width="1.8" stroke-linecap="round"><path d="M15 7h2a5 5 0 0 1 0 10h-2m-6 0H7A5 5 0 0 1 7 7h2"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
						{:else if f.icon === 'letter'}
							<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{f.color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
						{:else if f.icon === 'chat'}
							<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{f.color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
						{:else if f.icon === 'pdf'}
							<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{f.color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
						{:else if f.icon === 'link'}
							<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{f.color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
						{/if}
					</div>
					<h3 class="feature-title">{f.title}</h3>
					<p class="feature-desc">{f.desc}</p>
				</div>
			{/each}
		</div>
	</section>

	<!-- How it works -->
	<section class="steps-section">
		<div class="section-header anim-fade-up" style="--delay: 0s">
			<span class="section-tag">How It Works</span>
			<h2 class="section-title">Three Steps to a<br/><span class="gradient-text">Better Resume</span></h2>
		</div>
		<div class="steps-grid">
			{#each steps as s, i}
				<div class="step-card anim-fade-up" style="--delay: {0.1 * i}s">
					<span class="step-num">{s.num}</span>
					<h3 class="step-title">{s.title}</h3>
					<p class="step-desc">{s.desc}</p>
				</div>
				{#if i < steps.length - 1}
					<div class="step-connector anim-fade-up" style="--delay: {0.1 * i + 0.05}s">
						<svg width="40" height="16" viewBox="0 0 40 16"><path d="M0 8h32l-6-6M32 8l-6 6" fill="none" stroke="var(--color-border)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
					</div>
				{/if}
			{/each}
		</div>
	</section>

	<!-- CTA -->
	<section class="cta-section">
		<div class="cta-card anim-fade-up" style="--delay: 0s">
			<h2 class="cta-title">Ready to Improve Your Resume?</h2>
			<p class="cta-desc">Join thousands of job seekers using AI to land their dream roles. Start analyzing for free.</p>
			<div class="cta-buttons">
				<a href="{base}/analyze" class="btn-primary btn-lg">
					Get Started Free
					<span class="btn-arrow">&rarr;</span>
				</a>
			</div>
		</div>
	</section>

	<!-- Footer -->
	<footer class="footer">
		<div class="footer-inner">
			<span class="footer-brand">Resume<span class="brand-iq">IQ</span></span>
			<span class="footer-copy">Built with AI. Designed for job seekers.</span>
		</div>
	</footer>
</div>

<style>
	/* ================================================================
	   ANIMATIONS
	   ================================================================ */
	@keyframes fadeUp {
		from { opacity: 0; transform: translateY(24px); }
		to { opacity: 1; transform: translateY(0); }
	}
	@keyframes float {
		0%, 100% { transform: translateY(0); }
		50% { transform: translateY(-12px); }
	}
	@keyframes pulse-glow {
		0%, 100% { opacity: 0.4; transform: scale(1); }
		50% { opacity: 0.7; transform: scale(1.05); }
	}
	@keyframes dash-draw {
		from { stroke-dasharray: 0, 100; }
	}
	@keyframes shimmer {
		0% { background-position: -200% center; }
		100% { background-position: 200% center; }
	}
	@keyframes dot-pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.4; }
	}

	.anim-fade-up {
		opacity: 0;
		transform: translateY(24px);
	}
	.mounted .anim-fade-up {
		animation: fadeUp 0.6s ease-out forwards;
		animation-delay: var(--delay, 0s);
	}

	/* ================================================================
	   LAYOUT
	   ================================================================ */
	.landing {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		overflow-x: hidden;
		background: var(--color-bg);
	}

	/* ================================================================
	   NAVBAR
	   ================================================================ */
	.nav {
		position: sticky;
		top: 0;
		z-index: 100;
		background: color-mix(in srgb, var(--color-surface) 80%, transparent);
		backdrop-filter: blur(16px);
		-webkit-backdrop-filter: blur(16px);
		border-bottom: 1px solid color-mix(in srgb, var(--color-border) 50%, transparent);
	}

	.nav-inner {
		display: flex;
		align-items: center;
		justify-content: space-between;
		max-width: 1120px;
		margin: 0 auto;
		padding: 0.875rem 2rem;
	}

	.nav-brand {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 1.25rem;
		font-weight: 800;
		color: var(--color-text);
		text-decoration: none;
		letter-spacing: -0.02em;
	}
	.nav-brand:hover { text-decoration: none; }

	.nav-brand-icon { color: var(--color-text-secondary); }

	.brand-iq { color: var(--color-primary); }

	.nav-actions {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}

	.nav-link {
		padding: 0.5rem 0.875rem;
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-secondary);
		text-decoration: none;
		border-radius: var(--radius-sm);
		transition: color 0.2s, background 0.2s;
		border: none;
		background: none;
		cursor: pointer;
		font-family: inherit;
	}
	.nav-link:hover {
		color: var(--color-text);
		background: var(--color-surface-hover);
		text-decoration: none;
	}

	.nav-btn-primary {
		padding: 0.5rem 1.25rem;
		font-size: 0.875rem;
		font-weight: 600;
		color: white;
		background: var(--color-primary);
		border-radius: var(--radius-full);
		text-decoration: none;
		transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
	}
	.nav-btn-primary:hover {
		background: var(--color-primary-hover);
		transform: translateY(-1px);
		box-shadow: 0 4px 12px color-mix(in srgb, var(--color-primary) 30%, transparent);
		text-decoration: none;
	}

	.theme-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 36px;
		height: 36px;
		border-radius: var(--radius-full);
		border: 1px solid var(--color-border);
		background: var(--color-surface);
		color: var(--color-text-secondary);
		cursor: pointer;
		transition: background 0.2s, color 0.2s, border-color 0.2s;
		margin-right: 0.25rem;
	}
	.theme-btn:hover {
		background: var(--color-surface-hover);
		color: var(--color-text);
		border-color: var(--color-text-muted);
	}

	/* ================================================================
	   HERO
	   ================================================================ */
	.hero {
		position: relative;
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 4rem 2rem 5rem;
		overflow: hidden;
	}

	.hero-glow {
		position: absolute;
		border-radius: 50%;
		filter: blur(80px);
		pointer-events: none;
		animation: pulse-glow 6s ease-in-out infinite;
	}
	.hero-glow-1 {
		width: 500px; height: 500px;
		top: -120px; left: -100px;
		background: color-mix(in srgb, var(--color-primary) 15%, transparent);
	}
	.hero-glow-2 {
		width: 400px; height: 400px;
		top: 40px; right: -80px;
		background: color-mix(in srgb, #8b5cf6 12%, transparent);
		animation-delay: 2s;
	}
	.hero-glow-3 {
		width: 300px; height: 300px;
		bottom: -60px; left: 30%;
		background: color-mix(in srgb, #06b6d4 10%, transparent);
		animation-delay: 4s;
	}

	.hero-content {
		position: relative;
		text-align: center;
		max-width: 720px;
		z-index: 1;
	}

	.badge {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.4rem 1rem 0.4rem 0.75rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-full);
		font-size: 0.8125rem;
		font-weight: 600;
		color: var(--color-text-secondary);
		margin-bottom: 1.75rem;
		box-shadow: var(--shadow-sm);
	}
	.badge-dot {
		width: 8px; height: 8px;
		background: #22c55e;
		border-radius: 50%;
		animation: dot-pulse 2s ease-in-out infinite;
	}

	.hero-title {
		font-size: 3.75rem;
		font-weight: 800;
		line-height: 1.1;
		color: var(--color-text);
		letter-spacing: -0.035em;
		margin-bottom: 1.5rem;
	}

	.gradient-text {
		background: linear-gradient(135deg, var(--color-primary), #8b5cf6, #06b6d4);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.hero-subtitle {
		font-size: 1.125rem;
		line-height: 1.75;
		color: var(--color-text-secondary);
		margin-bottom: 2.5rem;
		max-width: 580px;
		margin-left: auto;
		margin-right: auto;
	}

	.hero-ctas {
		display: flex;
		justify-content: center;
		gap: 1rem;
		flex-wrap: wrap;
	}

	/* Buttons */
	.btn-primary {
		display: inline-flex;
		align-items: center;
		gap: 0.625rem;
		padding: 0.875rem 2rem;
		background: var(--color-primary);
		color: white;
		font-size: 1rem;
		font-weight: 600;
		border-radius: var(--radius-full);
		text-decoration: none;
		transition: background 0.2s, transform 0.15s, box-shadow 0.25s;
		box-shadow: 0 2px 8px color-mix(in srgb, var(--color-primary) 25%, transparent);
	}
	.btn-primary:hover {
		background: var(--color-primary-hover);
		transform: translateY(-2px);
		box-shadow: 0 8px 24px color-mix(in srgb, var(--color-primary) 35%, transparent);
		text-decoration: none;
	}
	.btn-primary:active { transform: translateY(0); }
	.btn-lg { padding: 1rem 2.5rem; font-size: 1.0625rem; }

	.btn-arrow {
		display: inline-block;
		transition: transform 0.2s;
	}
	.btn-primary:hover .btn-arrow { transform: translateX(4px); }

	.btn-secondary {
		display: inline-flex;
		align-items: center;
		padding: 0.875rem 2rem;
		background: var(--color-surface);
		color: var(--color-text);
		font-size: 1rem;
		font-weight: 600;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-full);
		text-decoration: none;
		transition: background 0.2s, border-color 0.2s, transform 0.15s;
	}
	.btn-secondary:hover {
		background: var(--color-surface-hover);
		border-color: var(--color-text-muted);
		transform: translateY(-1px);
		text-decoration: none;
	}

	/* ================================================================
	   HERO VISUAL (Mock Card)
	   ================================================================ */
	.hero-visual {
		position: relative;
		z-index: 1;
		margin-top: 3rem;
		animation: float 5s ease-in-out infinite;
		animation-delay: 1s;
	}

	.mock-card {
		width: 420px;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		box-shadow: var(--shadow-lg), 0 0 0 1px color-mix(in srgb, var(--color-border) 50%, transparent);
		overflow: hidden;
	}
	.mock-header {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem 1rem;
		background: var(--color-surface-hover);
		border-bottom: 1px solid var(--color-border);
	}
	.mock-dots { display: flex; gap: 5px; }
	.mock-dots span {
		width: 10px; height: 10px;
		border-radius: 50%;
		background: var(--color-border);
	}
	.mock-dots span:nth-child(1) { background: #ef4444; }
	.mock-dots span:nth-child(2) { background: #f59e0b; }
	.mock-dots span:nth-child(3) { background: #22c55e; }
	.mock-title { font-size: 0.75rem; color: var(--color-text-muted); font-weight: 500; }

	.mock-body { padding: 1.25rem; }
	.mock-score-row { display: flex; justify-content: center; gap: 2rem; margin-bottom: 1rem; }
	.mock-score { text-align: center; position: relative; }
	.mock-ring { width: 64px; height: 64px; transform: rotate(-90deg); }
	.mock-ring-bg { stroke: var(--color-border); }
	.mock-ring-fill {
		stroke: var(--color-primary);
		stroke-linecap: round;
		transition: stroke-dasharray 1s ease-out;
	}
	.mounted .mock-ring-fill { animation: dash-draw 1.5s ease-out forwards; animation-delay: 0.8s; }
	.ring-green { stroke: #22c55e; }
	.mock-score-val { display: block; font-size: 1.125rem; font-weight: 800; color: var(--color-text); margin-top: 0.25rem; }
	.mock-score-label { font-size: 0.6875rem; color: var(--color-text-muted); font-weight: 500; }

	.mock-tags { display: flex; flex-wrap: wrap; gap: 0.375rem; margin-bottom: 1rem; justify-content: center; }
	.mock-tag {
		padding: 0.25rem 0.625rem;
		font-size: 0.6875rem;
		font-weight: 600;
		border-radius: var(--radius-full);
	}
	.tag-green { background: var(--color-success-light); color: var(--color-success); }
	.tag-red { background: var(--color-danger-light); color: var(--color-danger); }

	.mock-bars { display: flex; flex-direction: column; gap: 0.5rem; }
	.mock-bar { display: flex; align-items: center; gap: 0.625rem; }
	.mock-bar-label { font-size: 0.6875rem; color: var(--color-text-muted); font-weight: 500; width: 65px; text-align: right; }
	.mock-bar-track { flex: 1; height: 6px; background: var(--color-surface-hover); border-radius: 3px; overflow: hidden; }
	.mock-bar-fill {
		height: 100%;
		background: var(--color-primary);
		border-radius: 3px;
		transition: width 1.2s ease-out;
	}
	.fill-purple { background: #8b5cf6; }
	.fill-cyan { background: #06b6d4; }

	/* ================================================================
	   STATS
	   ================================================================ */
	.stats-section {
		padding: 3rem 2rem;
		border-top: 1px solid var(--color-border);
		border-bottom: 1px solid var(--color-border);
		background: var(--color-surface);
	}
	.stats-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 2rem;
		max-width: 800px;
		margin: 0 auto;
		text-align: center;
	}
	.stat-value {
		display: block;
		font-size: 2rem;
		font-weight: 800;
		color: var(--color-text);
		letter-spacing: -0.02em;
		line-height: 1.2;
	}
	.stat-label {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		font-weight: 500;
		margin-top: 0.25rem;
		display: block;
	}

	/* ================================================================
	   FEATURES
	   ================================================================ */
	.features-section {
		padding: 5rem 2rem;
	}

	.section-header {
		text-align: center;
		margin-bottom: 3.5rem;
	}
	.section-tag {
		display: inline-block;
		padding: 0.375rem 1rem;
		background: color-mix(in srgb, var(--color-primary) 10%, transparent);
		color: var(--color-primary);
		border-radius: var(--radius-full);
		font-size: 0.8125rem;
		font-weight: 600;
		letter-spacing: 0.025em;
		margin-bottom: 1rem;
		border: 1px solid color-mix(in srgb, var(--color-primary) 15%, transparent);
	}
	.section-title {
		font-size: 2.5rem;
		font-weight: 800;
		color: var(--color-text);
		line-height: 1.2;
		letter-spacing: -0.03em;
		margin-bottom: 1rem;
	}
	.section-desc {
		font-size: 1.0625rem;
		color: var(--color-text-secondary);
		line-height: 1.6;
		max-width: 520px;
		margin: 0 auto;
	}

	.features-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 1.25rem;
		max-width: 1040px;
		margin: 0 auto;
	}

	.feature-card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: 1.5rem;
		transition: transform 0.25s, box-shadow 0.25s, border-color 0.25s;
		position: relative;
		overflow: hidden;
	}
	.feature-card::before {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		height: 3px;
		background: var(--accent);
		opacity: 0;
		transition: opacity 0.25s;
	}
	.feature-card:hover {
		transform: translateY(-4px);
		box-shadow: 0 12px 32px -8px color-mix(in srgb, var(--accent) 15%, transparent), var(--shadow-md);
		border-color: color-mix(in srgb, var(--accent) 30%, var(--color-border));
	}
	.feature-card:hover::before { opacity: 1; }

	.feature-icon-wrap {
		width: 44px;
		height: 44px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 12px;
		background: color-mix(in srgb, var(--accent) 10%, transparent);
		margin-bottom: 1rem;
		transition: transform 0.25s;
	}
	.feature-card:hover .feature-icon-wrap { transform: scale(1.1); }

	.feature-title {
		font-size: 0.9375rem;
		font-weight: 700;
		color: var(--color-text);
		margin-bottom: 0.5rem;
	}
	.feature-desc {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		line-height: 1.5;
	}

	/* ================================================================
	   STEPS
	   ================================================================ */
	.steps-section {
		padding: 5rem 2rem;
		background: var(--color-surface);
		border-top: 1px solid var(--color-border);
	}
	.steps-grid {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 1.5rem;
		max-width: 900px;
		margin: 0 auto;
	}
	.step-card {
		flex: 1;
		max-width: 240px;
		text-align: center;
		padding: 2rem 1.25rem;
		background: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		transition: transform 0.25s, box-shadow 0.25s;
	}
	.step-card:hover {
		transform: translateY(-4px);
		box-shadow: var(--shadow-lg);
	}
	.step-num {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 44px;
		height: 44px;
		border-radius: var(--radius-full);
		background: var(--color-primary);
		color: white;
		font-size: 0.9375rem;
		font-weight: 800;
		margin-bottom: 1rem;
	}
	.step-title {
		font-size: 1.0625rem;
		font-weight: 700;
		color: var(--color-text);
		margin-bottom: 0.5rem;
	}
	.step-desc {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		line-height: 1.5;
	}
	.step-connector {
		display: flex;
		align-items: center;
		flex-shrink: 0;
	}

	/* ================================================================
	   CTA
	   ================================================================ */
	.cta-section {
		padding: 5rem 2rem;
	}
	.cta-card {
		max-width: 680px;
		margin: 0 auto;
		text-align: center;
		padding: 3.5rem 2.5rem;
		background: linear-gradient(135deg, color-mix(in srgb, var(--color-primary) 8%, var(--color-surface)), color-mix(in srgb, #8b5cf6 6%, var(--color-surface)));
		border: 1px solid color-mix(in srgb, var(--color-primary) 20%, var(--color-border));
		border-radius: 20px;
		position: relative;
		overflow: hidden;
	}
	.cta-card::before {
		content: '';
		position: absolute;
		top: -1px;
		left: 20%;
		right: 20%;
		height: 2px;
		background: linear-gradient(90deg, transparent, var(--color-primary), #8b5cf6, transparent);
	}
	.cta-title {
		font-size: 2rem;
		font-weight: 800;
		color: var(--color-text);
		letter-spacing: -0.02em;
		margin-bottom: 0.75rem;
	}
	.cta-desc {
		font-size: 1.0625rem;
		color: var(--color-text-secondary);
		line-height: 1.6;
		margin-bottom: 2rem;
	}
	.cta-buttons { display: flex; justify-content: center; }

	/* ================================================================
	   FOOTER
	   ================================================================ */
	.footer {
		padding: 2rem;
		border-top: 1px solid var(--color-border);
	}
	.footer-inner {
		display: flex;
		align-items: center;
		justify-content: space-between;
		max-width: 1040px;
		margin: 0 auto;
	}
	.footer-brand {
		font-size: 1rem;
		font-weight: 800;
		color: var(--color-text);
	}
	.footer-copy {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
	}

	/* ================================================================
	   RESPONSIVE
	   ================================================================ */
	@media (max-width: 900px) {
		.features-grid { grid-template-columns: repeat(2, 1fr); }
		.hero-title { font-size: 2.75rem; }
		.section-title { font-size: 2rem; }
	}
	@media (max-width: 768px) {
		.hero { padding: 2.5rem 1.5rem 3rem; }
		.hero-title { font-size: 2.25rem; }
		.hero-subtitle { font-size: 1rem; }
		.mock-card { width: 340px; }
		.stats-grid { grid-template-columns: repeat(2, 1fr); gap: 1.5rem; }
		.steps-grid { flex-direction: column; gap: 1rem; }
		.step-connector { transform: rotate(90deg); }
		.step-card { max-width: 100%; width: 100%; }
		.nav-inner { padding: 0.75rem 1rem; }
		.nav-link { padding: 0.375rem 0.5rem; font-size: 0.8125rem; }
		.footer-inner { flex-direction: column; gap: 0.5rem; text-align: center; }
		.cta-title { font-size: 1.5rem; }
	}
	@media (max-width: 480px) {
		.hero-title { font-size: 1.875rem; }
		.section-title { font-size: 1.625rem; }
		.features-grid { grid-template-columns: 1fr; }
		.mock-card { width: 100%; max-width: 340px; }
		.hero-ctas { flex-direction: column; align-items: center; }
		.btn-primary, .btn-secondary { width: 100%; justify-content: center; max-width: 300px; }
		.stats-grid { grid-template-columns: repeat(2, 1fr); }
		.nav-actions { gap: 0.125rem; }
		.cta-card { padding: 2.5rem 1.5rem; }
	}
</style>
