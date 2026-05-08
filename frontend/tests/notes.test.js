import { describe, it, expect, vi, afterEach } from 'vitest';
import * as clientModule from '../src/api/client.js';
import {
  fetchNotes,
  fetchNote,
  fetchTags,
  createNote,
  updateNote,
  deleteNote,
  toggleBookmark,
  fallbackNote,
} from '../src/api/notes.js';

// Mock the entire client module so we can assert calls + simulate results/errors
vi.mock('../src/api/client.js', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('notes — API wrappers (delegation to client)', () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it('fetchNotes — calls api.get("/notes/", params)', async () => {
    const params = { q: 'react', page: 1 };
    clientModule.api.get.mockResolvedValue([{ id: 1 }]);
    const result = await fetchNotes(params);
    expect(result).toEqual([{ id: 1 }]);
    expect(clientModule.api.get).toHaveBeenCalledWith('/notes/', params);
  });

  it('fetchNote — calls api.get("/notes/{slug}/")', async () => {
    clientModule.api.get.mockResolvedValue({ id: 42, title: 'Hello' });
    const result = await fetchNote('hello-world');
    expect(result).toEqual({ id: 42, title: 'Hello' });
    expect(clientModule.api.get).toHaveBeenCalledWith('/notes/hello-world/');
  });

  it('fetchTags — calls api.get("/tags/", params)', async () => {
    clientModule.api.get.mockResolvedValue(['javascript', 'react']);
    const result = await fetchTags({});
    expect(result).toEqual(['javascript', 'react']);
    expect(clientModule.api.get).toHaveBeenCalledWith('/tags/', {});
  });

  it('createNote — calls api.post("/notes/", payload)', async () => {
    const payload = { title: 'New', content: 'body' };
    clientModule.api.post.mockResolvedValue({ id: 1, ...payload });
    const result = await createNote(payload);
    expect(result).toEqual({ id: 1, title: 'New', content: 'body' });
    expect(clientModule.api.post).toHaveBeenCalledWith('/notes/', payload);
  });

  it('updateNote — calls api.patch("/notes/{slug}/", payload)', async () => {
    const payload = { title: 'Updated' };
    clientModule.api.patch.mockResolvedValue({ slug: 'foo', ...payload });
    const result = await updateNote('foo', payload);
    expect(result).toEqual({ slug: 'foo', title: 'Updated' });
    expect(clientModule.api.patch).toHaveBeenCalledWith('/notes/foo/', payload);
  });

  it('deleteNote — calls api.delete("/notes/{slug}/")', async () => {
    clientModule.api.delete.mockResolvedValue(null);
    const result = await deleteNote('to-delete');
    expect(result).toBeNull();
    expect(clientModule.api.delete).toHaveBeenCalledWith('/notes/to-delete/');
  });

  it('toggleBookmark — calls api.post("/notes/{slug}/toggle_bookmark/")', async () => {
    clientModule.api.post.mockResolvedValue({ bookmark: true });
    const result = await toggleBookmark('my-note');
    expect(result).toEqual({ bookmark: true });
    expect(clientModule.api.post).toHaveBeenCalledWith('/notes/my-note/toggle_bookmark/');
  });
});

describe('fallbackNote — error resilience', () => {
  it('returns a placeholder object with the given slug', () => {
    const fb = fallbackNote('some-slug');
    expect(fb.slug).toBe('some-slug');
    expect(fb.title).toBe('some-slug');
    expect(fb.content).toContain('読み込めません');
    expect(fb.note_tags).toEqual([]);
  });

  it('uses default title when slug is empty string', () => {
    const fb = fallbackNote('');
    expect(fb.title).toBe('（読み込み失敗）');
    expect(fb.slug).toBe('');
  });

  it('uses default title when slug is null/undefined', () => {
    const fb1 = fallbackNote(null);
    const fb2 = fallbackNote(undefined);
    expect(fb1.title).toBe('（読み込み失敗）');
    expect(fb2.title).toBe('（読み込み失敗）');
  });

  it('returns a stable shape every time', () => {
    const fb = fallbackNote('test');
    expect(fb).toHaveProperty('slug');
    expect(fb).toHaveProperty('title');
    expect(fb).toHaveProperty('content');
    expect(fb).toHaveProperty('note_tags');
    expect(fb).toHaveProperty('has_mermaid');
    expect(fb).toHaveProperty('category_name');
    expect(fb).toHaveProperty('bookmark');
    expect(fb).toHaveProperty('status');
    expect(fb).toHaveProperty('updated_at');
  });
});
