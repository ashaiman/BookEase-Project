
export const API_BASE = import.meta.env.VITE_API_URL;

export async function apiRequest(path, options = {}) {
	const headers = {
		'Content-Type': 'application/json',
		...(options.headers || {})
	};

	const token = localStorage.getItem('token');
	if (token) {
		headers.Authorization = `Bearer ${token}`;
	}

	const response = await fetch(`${API_BASE}${path}`, {
		...options,
		headers
	});

	const text = await response.text();
	const data = text ? JSON.parse(text) : null;

	if (!response.ok) {
		throw new Error(data?.message || 'Request failed');
	}

	return data;
}
