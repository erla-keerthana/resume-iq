<script lang="ts">
	import '../app.css';
	import { base } from '$app/paths';
	import { goto } from '$app/navigation';
	import { auth, theme } from '$lib/stores.svelte';
	import { onMount } from 'svelte';
	import { page } from '$app/state';

	let { children } = $props();

	onMount(() => {
		auth.init();
		theme.init();
	});

	let currentPath = $derived(page.url?.pathname || '/');
	let showNav = $derived(currentPath !== `${base}/` && currentPath !== `${base}`);
</script>

<svelte:head>
	<meta name="description" content="AI-powered resume analyzer - get ATS scores, match analysis, and improvement suggestions" />
</svelte:head>

<div class="app">
	{#if showNav}
		<nav class="navbar">
			<div class="navbar-inner">
				<a class="nav-logo" href="{base}/">
					<svg class="nav-logo-icon" width="24" height="24" viewBox="0 0 24 24" fill="none">
						<rect x="3" y="2" width="18" height="20" rx="3" stroke="currentColor" stroke-width="1.5"/>
						<path d="M7 7h10M7 11h7M7 15h5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
						<circle cx="17" cy="17" r="4" fill="var(--color-primary)" stroke="var(--color-primary)" stroke-width="1"/>
						<path d="M15.5 17l1 1 2-2" stroke="white" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
					Resume<span class="nav-logo-iq">IQ</span>
				</a>
				<div class="nav-links">
					<a href="{base}/analyze" class="nav-link" class:active={currentPath.includes('/analyze')}>Analyze</a>
					<a href="{base}/dashboard" class="nav-link" class:active={currentPath.includes('/dashboard')}>Dashboard</a>
					<button class="theme-toggle" onclick={() => theme.toggle()} aria-label="Toggle dark mode">
						{#if theme.dark}
							<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
						{:else}
							<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
						{/if}
					</button>
					{#if auth.isLoggedIn}
						<div class="nav-user">
							<span class="nav-username">{auth.user?.username || auth.user?.name || 'User'}</span>
							<button class="nav-link logout-btn" onclick={() => { auth.logout(); goto(`${base}/login`); }}>Logout</button>
						</div>
					{:else}
						<a href="{base}/login" class="nav-link" class:active={currentPath.includes('/login')}>Login</a>
						<a href="{base}/signup" class="signup-link">Sign Up</a>
					{/if}
				</div>
			</div>
		</nav>
	{/if}
	{@render children()}
</div>

<style>
	.app {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	.navbar {
		position: sticky;
		top: 0;
		z-index: 100;
		background: color-mix(in srgb, var(--color-surface) 80%, transparent);
		backdrop-filter: blur(16px);
		-webkit-backdrop-filter: blur(16px);
		border-bottom: 1px solid color-mix(in srgb, var(--color-border) 50%, transparent);
	}

	.navbar-inner {
		display: flex;
		align-items: center;
		justify-content: space-between;
		max-width: 1120px;
		margin: 0 auto;
		padding: 0.75rem 2rem;
	}

	.nav-logo {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 1.25rem;
		font-weight: 800;
		color: var(--color-text);
		letter-spacing: -0.02em;
		text-decoration: none;
	}

	.nav-logo:hover { text-decoration: none; }

	.nav-logo-icon { color: var(--color-text-secondary); }

	.nav-logo-iq { color: var(--color-primary); }

	.nav-links {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}

	.nav-link {
		padding: 0.5rem 0.875rem;
		border-radius: var(--radius-sm);
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text-secondary);
		text-decoration: none;
		transition: background 0.2s, color 0.2s;
		border: none;
		background: none;
		cursor: pointer;
		font-family: inherit;
	}

	.nav-link:hover {
		background: var(--color-surface-hover);
		color: var(--color-text);
		text-decoration: none;
	}

	.nav-link.active {
		color: var(--color-primary);
		background: color-mix(in srgb, var(--color-primary) 10%, transparent);
	}

	.theme-toggle {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 36px;
		height: 36px;
		border: 1px solid var(--color-border);
		border-radius: 9999px;
		background: var(--color-surface);
		color: var(--color-text-secondary);
		cursor: pointer;
		transition: background 0.2s, color 0.2s, border-color 0.2s;
	}

	.theme-toggle:hover {
		background: var(--color-surface-hover);
		color: var(--color-text);
		border-color: var(--color-text-muted);
	}

	.nav-user {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}

	.nav-username {
		font-size: 0.8125rem;
		font-weight: 600;
		color: var(--color-text);
		padding: 0.5rem 0.625rem;
	}

	.signup-link {
		padding: 0.5rem 1.25rem;
		background: var(--color-primary);
		color: white;
		font-size: 0.875rem;
		font-weight: 600;
		border-radius: 9999px;
		text-decoration: none;
		transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
	}

	.signup-link:hover {
		background: var(--color-primary-hover);
		transform: translateY(-1px);
		box-shadow: 0 4px 12px color-mix(in srgb, var(--color-primary) 30%, transparent);
		text-decoration: none;
	}

	.logout-btn {
		background: none;
		border: none;
		cursor: pointer;
		font-family: inherit;
	}

	@media (max-width: 640px) {
		.navbar-inner { padding: 0.75rem 1rem; }
		.nav-links { gap: 0.125rem; }
		.nav-link { padding: 0.375rem 0.5rem; font-size: 0.8125rem; }
		.signup-link { padding: 0.375rem 0.875rem; font-size: 0.8125rem; }
	}
</style>
