import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { api } from '../src/api/client.js';

const API_BASE = '/api/v1';

describe('client — request() core', () => {
  let fetchMock;

  beforeEach(() => {
    fetchMock = vi.fn();
    globalThis.fetch = fetchMock;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // ─── Success ───

  it('returns parsed JSON on 200', async () => {
    fetchMock.mockResolvedValue({ ok: true, status: 200, json: () => Promise.resolve({ id: 1 }) });
    const result = await api.get('/notes/1');
    expect(result).toEqual({ id: 1 });
    expect(fetchMock).toHaveBeenCalledWith(`${API_BASE}/notes/1`, expect.objectContaining({}));
  });

  it('returns null on 204', async () => {
    fetchMock.mockResolvedValue({ ok: true, status: 204, json: vi.fn() });
    const result = await api.delete('/notes/1');
    expect(result).toBeNull();
  });

  // ─── HTTP errors (4xx/5xx) ───

  it('throws with error.message on 400', async () => {
    const body = { error: { message: 'bad request' } };
    fetchMock.mockResolvedValue({ ok: false, status: 400, json: () => Promise.resolve(body) });
    await expect(api.get('/notes')).rejects.toThrow('bad request');
  });

  it('throws with error.message on 500', async () => {
    const body = { error: { message: 'server error' } };
    fetchMock.mockResolvedValue({ ok: false, status: 500, json: () => Promise.resolve(body) });
    await expect(api.get('/notes')).rejects.toThrow('server error');
  });

  it('falls back to body.detail when error.message is absent', async () => {
    const body = { detail: 'not found' };
    fetchMock.mockResolvedValue({ ok: false, status: 404, json: () => Promise.resolve(body) });
    await expect(api.get('/notes/999')).rejects.toThrow('not found');
  });

  it('falls back to statusText when response is not JSON', async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      status: 502,
      statusText: 'Bad Gateway',
      json: () => Promise.reject(new Error('not json')),
    });
    await expect(api.get('/notes')).rejects.toThrow('Bad Gateway');
  });

  it('falls back to "HTTP {status}" when no body and no statusText', async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      status: 418,
      statusText: '',
      json: () => Promise.resolve(null),
    });
    await expect(api.get('/notes')).rejects.toThrow('HTTP 418');
  });

  // ─── Network errors ───

  it('throws on network failure (fetch rejects)', async () => {
    fetchMock.mockRejectedValue(new TypeError('Failed to fetch'));
    await expect(api.get('/notes')).rejects.toThrow('Failed to fetch');
  });

  // ─── Headers ───

  it('sets Content-Type: application/json by default', async () => {
    fetchMock.mockResolvedValue({ ok: true, status: 200, json: () => Promise.resolve({}) });
    await api.get('/notes');
    const [, config] = fetchMock.mock.calls[0];
    expect(config.headers['Content-Type']).toBe('application/json');
  });
});

describe('client — api convenience methods', () => {
  let fetchMock;

  beforeEach(() => {
    fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200, json: () => Promise.resolve({ data: 'ok' }) });
    globalThis.fetch = fetchMock;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // ─── GET ───

  it('api.get() — no query params', async () => {
    const result = await api.get('/notes');
    expect(result).toEqual({ data: 'ok' });
    expect(fetchMock).toHaveBeenCalledWith(`${API_BASE}/notes`, expect.objectContaining({}));
  });

  it('api.get() — with query params', async () => {
    await api.get('/notes', { q: 'react', page: 1 });
    const [url] = fetchMock.mock.calls[0];
    expect(url).toMatch(/\/api\/v1\/notes\?/);
    expect(url).toMatch(/q=react/);
    expect(url).toMatch(/page=1/);
  });

  it('api.get() — with pagination params that include null/undefined', async () => {
    await api.get('/notes', { tag: 'javascript', page: 2 });
    const [url] = fetchMock.mock.calls[0];
    expect(url).toMatch(/tag=javascript/);
    expect(url).toMatch(/page=2/);
  });

  // ─── POST ───

  it('api.post() — sends JSON body with POST method', async () => {
    const payload = { title: 'hello', content: 'world' };
    await api.post('/notes', payload);
    const [url, config] = fetchMock.mock.calls[0];
    expect(url).toBe(`${API_BASE}/notes`);
    expect(config.method).toBe('POST');
    expect(JSON.parse(config.body)).toEqual(payload);
  });

  // ─── PUT ───

  it('api.put() — sends JSON body with PUT method', async () => {
    const payload = { title: 'updated' };
    await api.put('/notes/1', payload);
    const [url, config] = fetchMock.mock.calls[0];
    expect(url).toBe(`${API_BASE}/notes/1`);
    expect(config.method).toBe('PUT');
    expect(JSON.parse(config.body)).toEqual(payload);
  });

  // ─── PATCH ───

  it('api.patch() — sends JSON body with PATCH method', async () => {
    const payload = { content: 'partial' };
    await api.patch('/notes/1', payload);
    const [url, config] = fetchMock.mock.calls[0];
    expect(url).toBe(`${API_BASE}/notes/1`);
    expect(config.method).toBe('PATCH');
    expect(JSON.parse(config.body)).toEqual(payload);
  });

  // ─── DELETE ───

  it('api.delete() — sends DELETE method with no body', async () => {
    fetchMock.mockResolvedValue({ ok: true, status: 204, json: vi.fn() });
    const result = await api.delete('/notes/1');
    expect(result).toBeNull();
    const [url, config] = fetchMock.mock.calls[0];
    expect(url).toBe(`${API_BASE}/notes/1`);
    expect(config.method).toBe('DELETE');
    expect(config.body).toBeUndefined();
  });
});
