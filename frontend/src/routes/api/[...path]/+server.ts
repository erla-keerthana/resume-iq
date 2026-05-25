import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

const BACKEND_URL = () => env.BACKEND_URL || 'http://backend:8001';

async function proxyToBackend(request: Request, backendPath: string): Promise<Response> {
	const url = `${BACKEND_URL()}/${backendPath}`;
	const headers: Record<string, string> = {};

	// Forward auth header
	const authHeader = request.headers.get('Authorization');
	if (authHeader) headers['Authorization'] = authHeader;

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
