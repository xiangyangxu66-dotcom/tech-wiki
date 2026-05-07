import { Suspense, lazy, useState, useEffect, useMemo } from 'react';
import TagCloud from './components/TagCloud';
import { fetchNote, fallbackNote } from './api/notes';
import './NotePage.css';

const MarkdownRenderer = lazy(() => import('./components/MarkdownRenderer'));

export default function NotePage({ slug }) {
    const [note, setNote] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        let cancelled = false;
        setLoading(true);
        setError(null);
        fetchNote(slug)
            .then(data => { if (!cancelled) setNote(data); })
            .catch(err => {
                if (!cancelled) {
                    console.error(err);
                    setError('ノートの読み込みに失敗しました');
                    setNote(fallbackNote(slug));
                }
            })
            .finally(() => { if (!cancelled) setLoading(false); });
        return () => { cancelled = true; };
    }, [slug]);

    const tags = useMemo(() => {
        if (!note?.note_tags) return [];
        return note.note_tags.map(tag => [tag, 1]);
    }, [note]);

    if (loading) {
        return (
            <div className="note-page">
                <div className="note-page-loading">読み込み中...</div>
            </div>
        );
    }

    const formattedDate = note?.updated_at
        ? new Date(note.updated_at).toLocaleDateString('ja-JP', {
            year: 'numeric', month: 'long', day: 'numeric'
        })
        : '';

    return (
        <div className="note-page">
            <nav className="note-page-nav">
                <div className="note-nav-actions">
                    <a href="/" className="back-link">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M10 3L5 8L10 13" stroke="currentColor" strokeWidth="1.5"
                                strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                        一覧に戻る
                    </a>
                    <a href={`/note/${slug}/edit`} className="note-edit-link">Edit</a>
                </div>
            </nav>

            <article className="note-detail">
                <header className="note-header">
                    <h1 className="note-title">{note.title}</h1>
                    <div className="note-meta">
                        {note.category_name && (
                            <span className="note-category">{note.category_name}</span>
                        )}
                        <span className="note-date">{formattedDate}</span>
                        {note.bookmark && (
                            <span className="note-bookmark">
                                <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                                    <path d="M6 1L7.5 4.2L11 4.7L8.4 7.2L9 10.7L6 9.1L3 10.7L3.6 7.2L1 4.7L4.5 4.2L6 1Z" />
                                </svg>
                                ブックマーク
                            </span>
                        )}
                        {note.status === 'draft' && (
                            <span className="note-draft">下書き</span>
                        )}
                    </div>

                    {tags.length > 0 && (
                        <div className="note-tags">
                            <TagCloud tags={tags} activeTag={null} onTagClick={() => { }} />
                        </div>
                    )}
                </header>

                {error && <div className="note-page-error">{error}</div>}

                <div className="note-body">
                    <Suspense fallback={<div className="note-page-loading">レンダリング中...</div>}>
                        <MarkdownRenderer
                            content={note.content || ''}
                            enableMermaid={Boolean(note.has_mermaid)}
                        />
                    </Suspense>
                </div>
            </article>
        </div>
    );
}
