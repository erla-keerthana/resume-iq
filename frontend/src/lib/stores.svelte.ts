import type { User } from './types';

// ---------------------------------------------------------------------------
// Auth Store — token lives in httpOnly cookie (not accessible to JS).
// On startup, we validate the cookie via /auth/me to restore the session.
// ---------------------------------------------------------------------------

let _user = $state<User | null>(null);
let _ready = $state(false);

function _loadAuth() {
	if (typeof window === 'undefined') return;
	const u = localStorage.getItem('resumeiq_user');
	if (u) {
		try {
			_user = JSON.parse(u);
		} catch {
			/* ignore */
		}
	}
}

export const auth = {
	get user() {
		return _user;
	},
	get isLoggedIn() {
		return !!_user;
	},
	get ready() {
		return _ready;
	},
	async init() {
		_loadAuth();
		// Clean up legacy token from localStorage (migration)
		if (typeof window !== 'undefined') {
			localStorage.removeItem('resumeiq_token');
			// Validate session via httpOnly cookie
			try {
				const { validateSession } = await import('./api');
				const user = await validateSession();
				if (user) {
					_user = user;
					localStorage.setItem('resumeiq_user', JSON.stringify(user));
				} else {
					_user = null;
					localStorage.removeItem('resumeiq_user');
				}
			} catch {
				// Network error: keep localStorage state as fallback
			}
		}
		_ready = true;
	},
	login(user: User) {
		_user = user;
		localStorage.setItem('resumeiq_user', JSON.stringify(user));
	},
	logout() {
		_user = null;
		localStorage.removeItem('resumeiq_user');
	}
};

// ---------------------------------------------------------------------------
// Theme Store (dark mode)
// ---------------------------------------------------------------------------

let _dark = $state(false);

function _loadTheme() {
	if (typeof window === 'undefined') return;
	const saved = localStorage.getItem('resumeiq_theme');
	if (saved === 'dark') {
		_dark = true;
	} else if (saved === 'light') {
		_dark = false;
	} else {
		_dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
	}
	_applyTheme();
}

function _applyTheme() {
	if (typeof document === 'undefined') return;
	document.documentElement.setAttribute('data-theme', _dark ? 'dark' : 'light');
}

export const theme = {
	get dark() {
		return _dark;
	},
	init() {
		_loadTheme();
	},
	toggle() {
		_dark = !_dark;
		localStorage.setItem('resumeiq_theme', _dark ? 'dark' : 'light');
		_applyTheme();
	}
};
