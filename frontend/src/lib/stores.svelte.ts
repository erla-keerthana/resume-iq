import type { User } from './types';

// ---------------------------------------------------------------------------
// Auth Store (uses localStorage for persistence)
// ---------------------------------------------------------------------------

let _token = $state<string | null>(null);
let _user = $state<User | null>(null);

function _loadAuth() {
	if (typeof window === 'undefined') return;
	const t = localStorage.getItem('resumeiq_token');
	const u = localStorage.getItem('resumeiq_user');
	if (t) _token = t;
	if (u) {
		try {
			_user = JSON.parse(u);
		} catch {
			/* ignore */
		}
	}
}

export const auth = {
	get token() {
		return _token;
	},
	get user() {
		return _user;
	},
	get isLoggedIn() {
		return !!_token && !!_user;
	},
	init() {
		_loadAuth();
	},
	login(token: string, user: User) {
		_token = token;
		_user = user;
		localStorage.setItem('resumeiq_token', token);
		localStorage.setItem('resumeiq_user', JSON.stringify(user));
	},
	logout() {
		_token = null;
		_user = null;
		localStorage.removeItem('resumeiq_token');
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
