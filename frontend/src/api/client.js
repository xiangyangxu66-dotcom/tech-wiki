const API_BASE = '/api/v1';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  };
  const res = await fetch(url, config);
  if (!res.ok) {
    let body;
    try { body = await res.json(); } catch (_) { body = null; }
    const msg = body?.error?.message || body?.detail || res.statusText;
    throw new Error(msg || `HTTP ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  get: (url, params) => {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    return request(url + query);
  },
  post: (url, data) => request(url, { method: 'POST', body: JSON.stringify(data) }),
  put: (url, data) => request(url, { method: 'PUT', body: JSON.stringify(data) }),
  patch: (url, data) => request(url, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (url) => request(url, { method: 'DELETE' }),
};
