export function resolveNoteRoute(locationLike = window.location) {
    const rawPath = locationLike.pathname || '/';
    const search = new URLSearchParams(locationLike.search || '');
    const path = rawPath.replace(/\/$/, '');

    if (path === '/note/new/edit') {
        return { isEdit: true, isNew: true, slug: null };
    }

    const legacySlug = search.get('slug');
    if (path === '/note.html' && legacySlug) {
        return { isEdit: false, isNew: false, slug: legacySlug };
    }

    const isEdit = /\/note\/.*\/edit$/.test(path);
    const routeMatch = path.match(/^\/note\/(.+?)(?:\/edit)?$/);

    return {
        isEdit,
        isNew: false,
        slug: routeMatch ? routeMatch[1] : null,
    };
}
