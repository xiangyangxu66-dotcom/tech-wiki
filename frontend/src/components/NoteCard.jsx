import './NoteCard.css';

const TECH_ICONS = {
    React: '⚛️', JavaScript: '🟨', TypeScript: '🔷', Python: '🐍',
    Django: '🧩', FastAPI: '⚡', Go: '🦫', Rust: '🦀',
    Docker: '🐳', Kubernetes: '☸️', AWS: '☁️', Linux: '🐧',
    MySQL: '🐬', PostgreSQL: '🐘', Redis: '🔴', MongoDB: '🍃',
    Node: '💚', 'Node.js': '💚', Git: '🔀', HTML: '🌐',
    CSS: '🎨', GraphQL: '◈', Nginx: '🟢',
};

function pickIcon(title, tags) {
    for (const tag of (tags || [])) {
        if (TECH_ICONS[tag]) return TECH_ICONS[tag];
    }
    for (const [key, value] of Object.entries(TECH_ICONS)) {
        if (title.includes(key)) return value;
    }
    return '📄';
}

function StarIcon({ filled, onClick }) {
    return (
        <button
            type="button"
            className={`bookmark-toggle-btn ${filled ? 'bookmarked' : ''}`}
            onClick={onClick}
            title={filled ? 'ブックマークを外す' : 'ブックマークする'}
            aria-label={filled ? 'ブックマークを外す' : 'ブックマークする'}
        >
            <svg width="13" height="13" viewBox="0 0 14 14" fill={filled ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="1.2">
                <path d="M7 1L8.8 4.8L13 5.4L9.9 8.3L10.6 12.5L7 10.6L3.4 12.5L4.1 8.3L1 5.4L5.2 4.8L7 1Z" />
            </svg>
        </button>
    );
}

export default function NoteCard({
    note,
    onBookmarkToggle,
    mode = 'list',
}) {
    const tags = note.note_tags || [];
    const icon = pickIcon(note.title, tags);
    const editorHref = `/note/${note.slug}/edit`;
    const formattedDate = note.updated_at
        ? new Date(note.updated_at).toLocaleDateString('ja-JP', {
            year: 'numeric', month: 'short', day: 'numeric'
        })
        : '';

    const handleBookmarkClick = (event) => {
        event.preventDefault();
        event.stopPropagation();
        if (onBookmarkToggle) onBookmarkToggle(note.slug);
    };

    if (mode === 'icon') {
        return (
            <a href={editorHref} className={`card-icon ${note.bookmark ? 'bookmarked' : ''}`}>
                <div className="card-icon-symbol">{icon}</div>
                <div className="card-icon-title" title={note.title}>{note.title}</div>
                <StarIcon filled={note.bookmark} onClick={handleBookmarkClick} />
            </a>
        );
    }

    return (
        <article
            className={`note-card ${note.bookmark ? 'bookmarked' : ''}`}
            onClick={() => { window.location.href = editorHref; }}
        >
            <a href={editorHref} className="card-icon-left">{icon}</a>
            <div className="card-body">
                <div className="card-header">
                    <StarIcon filled={note.bookmark} onClick={handleBookmarkClick} />
                    <h3 className="card-title">
                        <a href={editorHref}>{note.title}</a>
                    </h3>
                </div>
                <div className="card-meta-row">
                    {note.category_name && (
                        <span className="card-category">{note.category_name}</span>
                    )}
                    {note.status === 'draft' && (
                        <span className="card-draft">下書き</span>
                    )}
                    <span className="card-date">{formattedDate}</span>
                </div>
                {note._snippet && (
                    <div
                        className="card-snippet"
                        dangerouslySetInnerHTML={{ __html: note._snippet }}
                    />
                )}
            </div>
        </article>
    );
}
