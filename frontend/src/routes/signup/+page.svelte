<script lang="ts">
	import { base } from '$app/paths';
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores.svelte';
	import { signup } from '$lib/api';

	let username = $state('');
	let email = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let loading = $state(false);
	let error = $state('');
	let mounted = $state(false);

	$effect(() => {
		if (auth.ready && auth.isLoggedIn) {
			goto(`${base}/dashboard`);
		}
		if (auth.ready && !auth.isLoggedIn) {
			requestAnimationFrame(() => { mounted = true; });
		}
	});

	function validate(): string | null {
		const u = username.trim();
		if (!u || u.length < 3) return 'Username must be at least 3 characters.';
		if (u.length > 30) return 'Username must be at most 30 characters.';
		if (!/^[a-zA-Z0-9_]+$/.test(u)) return 'Username can only contain letters, numbers, and underscores.';
		if (!email.trim()) return 'Please enter your email address.';
		if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) return 'Please enter a valid email address.';
		if (password.length < 8) return 'Password must be at least 8 characters.';
		if (password !== confirmPassword) return 'Passwords do not match.';
		return null;
	}

	async function handleSignup(e: Event) {
		e.preventDefault();
		error = '';

		const validationError = validate();
		if (validationError) {
			error = validationError;
			return;
		}

		loading = true;
		try {
			const result = await signup(username.trim(), email.trim(), password);
			auth.login(result.user);
			goto(`${base}/dashboard`);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Signup failed. Please try again.';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Sign Up - ResumeIQ</title>
</svelte:head>

{#if auth.ready && !auth.isLoggedIn}
<div class="page" class:mounted>
	<!-- Decorative glow orbs -->
	<div class="glow glow-1"></div>
	<div class="glow glow-2"></div>

	<main class="signup-container">
		<div class="signup-card anim-fade-up" style="--delay: 0s">
			<!-- Brand header -->
			<div class="signup-header anim-fade-up" style="--delay: 0.1s">
				<div class="brand-icon">
					<svg width="40" height="40" viewBox="0 0 24 24" fill="none">
						<rect x="3" y="2" width="18" height="20" rx="3" stroke="var(--color-primary)" stroke-width="1.5"/>
						<path d="M7 7h10M7 11h7M7 15h5" stroke="var(--color-primary)" stroke-width="1.5" stroke-linecap="round"/>
						<circle cx="17" cy="17" r="4" fill="var(--color-primary)"/>
						<path d="M15.5 17l1 1 2-2" stroke="white" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
				</div>
				<h1>Create Your <span class="gradient-text">Account</span></h1>
				<p>Join ResumeIQ and start optimizing your resume</p>
			</div>

			{#if error}
				<div class="error-msg anim-fade-up" style="--delay: 0.15s">
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
					</svg>
					{error}
				</div>
			{/if}

			<form class="signup-form" onsubmit={handleSignup}>
				<div class="form-group anim-fade-up" style="--delay: 0.15s">
					<label for="username">
						<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
						Username
					</label>
					<input
						id="username"
						type="text"
						bind:value={username}
						placeholder="johndoe"
						autocomplete="username"
						disabled={loading}
					/>
				</div>

				<div class="form-group anim-fade-up" style="--delay: 0.2s">
					<label for="email">
						<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
						Email
					</label>
					<input
						id="email"
						type="email"
						bind:value={email}
						placeholder="you@example.com"
						autocomplete="email"
						disabled={loading}
					/>
				</div>

				<div class="form-group anim-fade-up" style="--delay: 0.25s">
					<label for="password">
						<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
						Password
					</label>
					<input
						id="password"
						type="password"
						bind:value={password}
						placeholder="At least 8 characters"
						autocomplete="new-password"
						disabled={loading}
					/>
				</div>

				<div class="form-group anim-fade-up" style="--delay: 0.3s">
					<label for="confirm-password">
						<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
						Confirm Password
					</label>
					<input
						id="confirm-password"
						type="password"
						bind:value={confirmPassword}
						placeholder="Re-enter your password"
						autocomplete="new-password"
						disabled={loading}
					/>
				</div>

				<button type="submit" class="submit-btn anim-fade-up" style="--delay: 0.35s" disabled={loading}>
					{#if loading}
						<span class="spinner"></span> Creating account...
					{:else}
						Create Account
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
					{/if}
				</button>
			</form>

			<p class="signup-footer anim-fade-up" style="--delay: 0.4s">
				Already have an account? <a href="{base}/login" class="link">Sign in</a>
			</p>
		</div>
	</main>
</div>
{/if}

<style>
	.page {
		min-height: 100vh;
		background: var(--color-bg);
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
		overflow: hidden;
	}

	/* Animated glow orbs */
	.glow {
		position: absolute;
		border-radius: 50%;
		filter: blur(80px);
		opacity: 0.35;
		pointer-events: none;
		animation: pulse-glow 6s ease-in-out infinite alternate;
	}
	.glow-1 {
		width: 400px; height: 400px;
		background: #8b5cf6;
		top: -100px; left: -100px;
		animation-delay: 0s;
	}
	.glow-2 {
		width: 350px; height: 350px;
		background: var(--color-primary);
		bottom: -80px; right: -80px;
		animation-delay: 3s;
	}

	@keyframes pulse-glow {
		0% { transform: scale(1); opacity: 0.25; }
		100% { transform: scale(1.15); opacity: 0.4; }
	}

	/* Fade-up animation */
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

	.signup-container {
		width: 100%;
		max-width: 440px;
		padding: 2rem;
		position: relative;
		z-index: 1;
	}

	.signup-card {
		background: color-mix(in srgb, var(--color-surface) 80%, transparent);
		backdrop-filter: blur(20px);
		-webkit-backdrop-filter: blur(20px);
		border-radius: var(--radius-lg);
		padding: 2.5rem 2rem;
		box-shadow: var(--shadow-lg), 0 0 0 1px color-mix(in srgb, var(--color-border) 50%, transparent);
		border: 1px solid color-mix(in srgb, var(--color-border) 60%, transparent);
	}

	/* Brand header */
	.signup-header {
		text-align: center;
		margin-bottom: 2rem;
	}
	.brand-icon {
		width: 64px;
		height: 64px;
		border-radius: 16px;
		background: color-mix(in srgb, var(--color-primary) 10%, transparent);
		display: flex;
		align-items: center;
		justify-content: center;
		margin: 0 auto 1rem;
		border: 1px solid color-mix(in srgb, var(--color-primary) 20%, transparent);
	}
	.signup-header h1 {
		font-size: 1.75rem;
		font-weight: 800;
		color: var(--color-text);
		margin-bottom: 0.375rem;
	}
	.gradient-text {
		background: linear-gradient(135deg, var(--color-primary), #8b5cf6);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}
	.signup-header p {
		font-size: 0.875rem;
		color: var(--color-text-muted);
	}

	/* Error */
	.error-msg {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 1rem;
		background: var(--color-danger-light);
		color: var(--color-danger);
		border-radius: var(--radius-md);
		font-size: 0.8125rem;
		font-weight: 500;
		margin-bottom: 1rem;
		border: 1px solid color-mix(in srgb, var(--color-danger) 20%, transparent);
	}

	/* Form */
	.signup-form { display: flex; flex-direction: column; gap: 1rem; }

	.form-group { display: flex; flex-direction: column; gap: 0.375rem; }
	.form-group label {
		font-size: 0.8125rem;
		font-weight: 600;
		color: var(--color-text-secondary);
		display: flex;
		align-items: center;
		gap: 0.375rem;
	}
	.form-group input {
		padding: 0.8125rem 1rem;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		font-size: 0.9375rem;
		background: color-mix(in srgb, var(--color-bg) 70%, transparent);
		color: var(--color-text);
		transition: border-color 0.2s, box-shadow 0.2s;
		font-family: inherit;
	}
	.form-group input:focus {
		outline: none;
		border-color: var(--color-primary);
		box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-primary) 15%, transparent);
	}
	.form-group input:disabled { opacity: 0.6; }
	.form-group input::placeholder { color: var(--color-text-muted); }

	/* Submit button */
	.submit-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		width: 100%;
		padding: 0.8125rem;
		background: linear-gradient(135deg, var(--color-primary), #4f46e5);
		color: white;
		border: none;
		border-radius: var(--radius-md);
		font-size: 0.9375rem;
		font-weight: 600;
		cursor: pointer;
		transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s;
		font-family: inherit;
		margin-top: 0.25rem;
		box-shadow: 0 4px 14px color-mix(in srgb, var(--color-primary) 35%, transparent);
	}
	.submit-btn:hover:not(:disabled) {
		transform: translateY(-1px);
		box-shadow: 0 6px 20px color-mix(in srgb, var(--color-primary) 45%, transparent);
	}
	.submit-btn:active:not(:disabled) { transform: translateY(0); }
	.submit-btn:disabled { opacity: 0.7; cursor: not-allowed; }

	.spinner {
		display: inline-block;
		width: 16px; height: 16px;
		border: 2px solid rgba(255,255,255,0.3);
		border-top-color: white;
		border-radius: 50%;
		animation: spin 0.7s linear infinite;
	}
	@keyframes spin { to { transform: rotate(360deg); } }

	/* Footer */
	.signup-footer {
		font-size: 0.8125rem;
		color: var(--color-text-muted);
		margin-top: 1.5rem;
		text-align: center;
	}
	.link {
		color: var(--color-primary);
		font-weight: 600;
		text-decoration: none;
		transition: color 0.15s;
	}
	.link:hover { text-decoration: underline; }

	@media (max-width: 480px) {
		.signup-container { padding: 1rem; }
		.signup-card { padding: 2rem 1.5rem; }
		.signup-header h1 { font-size: 1.5rem; }
		.glow-1 { width: 250px; height: 250px; }
		.glow-2 { width: 200px; height: 200px; }
	}
</style>
