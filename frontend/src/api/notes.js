import { api } from './client';

export const fetchNotes = (params) => api.get('/notes/', params);
export const fetchNote = (slug) => api.get(`/notes/${slug}/`);
export const fetchTags = () => api.get('/tags/');
export const createNote = (payload) => api.post('/notes/', payload);
export const updateNote = (slug, payload) => api.patch(`/notes/${slug}/`, payload);
export const deleteNote = (slug) => api.delete(`/notes/${slug}/`);

export const toggleBookmark = (slug) => api.post(`/notes/${slug}/toggle_bookmark/`);

export function fallbackNote(slug) {
    return {
        title: slug || '（読み込み失敗）',
        slug,
        content: '> このノートは現在読み込めません。',
        note_tags: [],
        has_mermaid: false,
        category_name: '',
        bookmark: false,
        status: 'draft',
        updated_at: null,
    };
}
