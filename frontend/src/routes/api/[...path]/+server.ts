import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

const BACKEND_URL = () => env.BACKEND_URL || 'http://backend:8001';
const COOKIE_NAME = 'resumeiq_session';
const COOKIE_MAX_AGE = 30 * 24 * 60 * 60; // 30 days (matches JWT expiry)

function parseCookies(cookieHeader: string): Record<string, string> {
	const cookies: Record<string, string> = {};
	for (const part of cookieHeader.split(';')) {
		const [k, ...v] = part.trim().split('=');
		if (k) cookies[k] = v.join('=');
	}
	return cookies;
}

async function proxyToBackend(request: Request, backendPath: string): Promise<Response> {
	const url = `${BACKEND_URL()}/${backendPath}`;
	const headers: Record<string, string> = {};

	// Read token from httpOnly cookie and forward as Authorization header to backend
	const cookieHeader = request.headers.get('Cookie') || '';
	const cookies = parseCookies(cookieHeader);
	const token = cookies[COOKIE_NAME];
	if (token) {
		headers['Authorization'] = `Bearer ${token}`;
	}

	let body: FormData | string | undefined;
	const contentType = request.headers.get('Content-Type') || '';

	if (contentType.includes('multipart/form-data') || contentType.includes('application/x-www-form-urlencoded')) {
		body = await request.formData();
	} else if (contentType.includes('application/json')) {
		body = await request.text();
		headers['Content-Type'] = 'application/json';
	}

	let backendResponse: Response;
	try {
		backendResponse = await fetch(url, {
			method: request.method,
			body: request.method !== 'GET' && request.method !== 'HEAD' ? body : undefined,
			headers
		});
	} catch {
		return new Response(
			JSON.stringify({ detail: 'Backend service is unavailable' }),
			{ status: 502, headers: { 'Content-Type': 'application/json' } }
		);
	}

	const responseHeaders: Record<string, string> = {
		'Content-Type': backendResponse.headers.get('Content-Type') || 'application/json'
	};

	// Forward Content-Disposition for file downloads
	const disposition = backendResponse.headers.get('Content-Disposition');
	if (disposition) responseHeaders['Content-Disposition'] = disposition;

	const data = await backendResponse.arrayBuffer();

	// For auth endpoints: extract token from response body, set as httpOnly cookie,
	// and return only the user object to the browser
	if (backendResponse.ok && (backendPath === 'auth/login' || backendPath === 'auth/signup')) {
		try {
			const json = JSON.parse(new TextDecoder().decode(data));
			if (json.token) {
				const secure = request.url.startsWith('https') ? '; Secure' : '';
				responseHeaders['Set-Cookie'] =
					`${COOKIE_NAME}=${json.token}; HttpOnly; SameSite=Lax; Path=/; Max-Age=${COOKIE_MAX_AGE}${secure}`;
				// Return user without the token — browser JS never sees it
				const clientBody = JSON.stringify({ user: json.user });
				return new Response(clientBody, { status: backendResponse.status, headers: responseHeaders });
			}
		} catch {
			// Fall through to normal response
		}
	}

	// For logout: clear the cookie
	if (backendPath === 'auth/logout') {
		responseHeaders['Set-Cookie'] =
			`${COOKIE_NAME}=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0`;
		return new Response(JSON.stringify({ ok: true }), { status: 200, headers: responseHeaders });
	}

	return new Response(data, { status: backendResponse.status, headers: responseHeaders });
}

export const GET: RequestHandler = async ({ request, params }) => {
	return proxyToBackend(request, params.path);
};

export const POST: RequestHandler = async ({ request, params }) => {
	return proxyToBackend(request, params.path);
};

export const DELETE: RequestHandler = async ({ request, params }) => {
	return proxyToBackend(request, params.path);
};
