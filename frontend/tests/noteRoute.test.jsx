import { describe, expect, it } from 'vitest';
import { resolveNoteRoute } from '../src/noteRoute';

describe('resolveNoteRoute', () => {
    it('resolves note detail path', () => {
        expect(resolveNoteRoute({ pathname: '/note/python-intro', search: '' })).toEqual({
            isEdit: false,
            isNew: false,
            slug: 'python-intro',
        });
    });

    it('resolves note edit path', () => {
        expect(resolveNoteRoute({ pathname: '/note/python-intro/edit', search: '' })).toEqual({
            isEdit: true,
            isNew: false,
            slug: 'python-intro',
        });
    });

    it('resolves new note path', () => {
        expect(resolveNoteRoute({ pathname: '/note/new/edit', search: '' })).toEqual({
            isEdit: true,
            isNew: true,
            slug: null,
        });
    });

    it('supports note html query route', () => {
        expect(resolveNoteRoute({ pathname: '/note.html', search: '?slug=python-intro' })).toEqual({
            isEdit: false,
            isNew: false,
            slug: 'python-intro',
        });
    });
});
