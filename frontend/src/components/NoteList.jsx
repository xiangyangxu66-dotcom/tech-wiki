import { useMemo, useState } from 'react';
import { toggleBookmark } from '../api/notes';
import NoteCard from './NoteCard';
import './NoteList.css';

const ITEMS_PER_PAGE_LIST = 10;

const ICON_ROWS_MAP = { 2: 5, 3: 3, 4: 3 };

const SORT_OPTIONS = [
    { key: 'updated', label: '更新日時', fn: (a, b) => new Date(b.updated_at) - new Date(a.updated_at) },
    { key: 'created', label: '作成日時', fn: (a, b) => new Date(b.created_at) - new Date(a.created_at) },
    { key: 'title', label: 'ファイル名', fn: (a, b) => a.title.localeCompare(b.title, 'ja') },
];

function extractSearchTerms(searchParams) {
    const terms = [];
    if (searchParams?.title) {
        const words = searchParams.title.trim().split(/\s+/);
        for (const w of words) if (w) terms.push(w);
    }
    if (searchParams?.content) {
        // Content uses REGEXP on backend; treat space-separated words as literal terms
        const words = searchParams.content.trim().split(/\s+/);
        for (const w of words) if (w) terms.push(w);
    }
    // Deduplicate (case-insensitive) — keep first occurrence
    const seen = new Set();
    return terms.filter(t => {
        const lower = t.toLowerCase();
        if (seen.has(lower)) return false;
        seen.add(lower);
        return true;
    });
}

export default function NoteList({ notes, loading, activeTag, onTagClick, onNotesChange, searchParams }) {
    const searchTerms = extractSearchTerms(searchParams);
    const [viewMode, setViewMode] = useState('list');
    const [listColumns, setListColumns] = useState(3);
    const [sortKey, setSortKey] = useState('updated');
    const [tagPages, setTagPages] = useState({});

    const notesPerPage = viewMode === 'icon'
        ? listColumns * ICON_ROWS_MAP[listColumns]
        : ITEMS_PER_PAGE_LIST;

    const safeNotes = notes || [];

    const sortFn = SORT_OPTIONS.find(option => option.key === sortKey)?.fn || SORT_OPTIONS[0].fn;

    const sorted = useMemo(() => {
        const items = [...safeNotes];
        items.sort(sortFn);
        return items;
    }, [safeNotes, sortFn]);

    const bookmarked = sorted.filter(note => note.bookmark);
    const rest = sorted.filter(note => !note.bookmark);

    const tagGroups = useMemo(() => {
        const grouped = new Map();
        for (const note of rest) {
            const tags = note.note_tags?.length ? note.note_tags : ['未分類タグ'];
            for (const tag of tags) {
                if (!grouped.has(tag)) grouped.set(tag, []);
                grouped.get(tag).push(note);
            }
        }
        return Array.from(grouped.entries());
    }, [rest]);

    const handleBookmarkToggle = async (slug) => {
        if (onNotesChange) {
            onNotesChange(prev => prev.map(note =>
                note.slug === slug ? { ...note, bookmark: !note.bookmark } : note
            ));
        }
        try {
            await toggleBookmark(slug);
        } catch {
            if (onNotesChange) {
                onNotesChange(prev => prev.map(note =>
                    note.slug === slug ? { ...note, bookmark: !note.bookmark } : note
                ));
            }
        }
    };

    if (loading) {
        return (
            <div className="note-list-loading">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" className="loading-spinner">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" opacity="0.2" />
                    <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                        <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="0.8s" repeatCount="indefinite" />
                    </path>
                </svg>
                <p>読み込み中...</p>
            </div>
        );
    }

    if (safeNotes.length === 0) {
        return (
            <div className="note-list-empty">
                <p>該当するノートがありません</p>
            </div>
        );
    }

    return (
        <div className="note-list">
            <div className="list-toolbar">
                <div className="list-toolbar-left">
                    <div className="view-toggle">
                        <button
                            className={`view-btn ${viewMode === 'icon' ? 'active' : ''}`}
                            onClick={() => setViewMode('icon')}
                            title="アイコン表示"
                        >
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                <rect x="1" y="1" width="6" height="6" rx="1.5" />
                                <rect x="9" y="1" width="6" height="6" rx="1.5" />
                                <rect x="1" y="9" width="6" height="6" rx="1.5" />
                                <rect x="9" y="9" width="6" height="6" rx="1.5" />
                            </svg>
                        </button>
                        <button
                            className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
                            onClick={() => setViewMode('list')}
                            title="リスト表示"
                        >
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                <rect x="1" y="2" width="14" height="2" rx="1" />
                                <rect x="1" y="7" width="14" height="2" rx="1" />
                                <rect x="1" y="12" width="14" height="2" rx="1" />
                            </svg>
                        </button>
                    </div>

                    {viewMode === 'list' && (
                        <div className="column-toggle" aria-label="列数切り替え">
                            {[2, 3, 4].map((cols) => (
                                <button
                                    key={cols}
                                    type="button"
                                    className={`column-btn ${listColumns === cols ? 'active' : ''}`}
                                    onClick={() => setListColumns(cols)}
                                >
                                    {cols}列
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                <div className="list-toolbar-right">
                    <a href="/note/new/edit" className="list-create-link">Note作成</a>
                    <select
                        className="sort-select"
                        value={sortKey}
                        onChange={(event) => setSortKey(event.target.value)}
                    >
                        {SORT_OPTIONS.map(option => (
                            <option key={option.key} value={option.key}>{option.label}</option>
                        ))}
                    </select>
                </div>
            </div>

            {bookmarked.length > 0 && (
                <section className="bookmark-section">
                    <div className="section-divider">
                        <span className="section-divider-label">
                            <span className="section-icon pin" aria-hidden="true">📌</span>
                            <span>ピン留め</span>
                        </span>
                    </div>
                    <div className={`note-cards ${viewMode === 'icon' ? 'icon-grid' : `list-grid cols-${listColumns}`}`}>
                        {bookmarked.map(note => (
                            <NoteCard
                                key={note.id}
                                note={note}
                                onBookmarkToggle={handleBookmarkToggle}
                                mode={viewMode}
                                searchTerms={searchTerms}
                            />
                        ))}
                    </div>
                </section>
            )}

            {tagGroups.map(([tagName, tagNotes]) => {
                const totalPages = Math.max(1, Math.ceil(tagNotes.length / notesPerPage));
                const currentPage = Math.min(tagPages[tagName] || 1, totalPages);
                const start = (currentPage - 1) * notesPerPage;
                const pageItems = tagNotes.slice(start, start + notesPerPage);

                return (
                    <section className="note-list-section" key={tagName}>
                        <div className="section-divider">
                            <span className="section-divider-label">
                                <span className={`section-icon ${tagName === '未分類タグ' ? 'untagged' : 'tag'}`} aria-hidden="true">
                                    {tagName === '未分類タグ' ? '○' : '#'}
                                </span>
                                <span>{tagName}</span>
                            </span>
                        </div>
                        <div className={`note-cards ${viewMode === 'icon' ? 'icon-grid' : `list-grid cols-${listColumns}`}`}>
                            {pageItems.map(note => (
                                <NoteCard
                                    key={`${tagName}-${note.id}`}
                                    note={note}
                                    onBookmarkToggle={handleBookmarkToggle}
                                    mode={viewMode}
                                    searchTerms={searchTerms}
                                />
                            ))}
                        </div>
                        {totalPages > 1 && (
                            <div className="tag-pagination">
                                <button
                                    type="button"
                                    className="pager-btn"
                                    disabled={currentPage <= 1}
                                    onClick={() => setTagPages((prev) => ({ ...prev, [tagName]: currentPage - 1 }))}
                                >
                                    前へ
                                </button>
                                <span className="pager-info">{currentPage} / {totalPages}</span>
                                <button
                                    type="button"
                                    className="pager-btn"
                                    disabled={currentPage >= totalPages}
                                    onClick={() => setTagPages((prev) => ({ ...prev, [tagName]: currentPage + 1 }))}
                                >
                                    次へ
                                </button>
                            </div>
                        )}
                    </section>
                );
            })}
        </div>
    );
}
