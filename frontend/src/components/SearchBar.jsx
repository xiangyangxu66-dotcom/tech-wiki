import { useState, useRef, useCallback } from 'react';
import './SearchBar.css';

/**
 * Two-column inline search bar with search button.
 *
 * Props:
 *   onSearch({ title, content }) — called on Enter or button click
 *
 * Layout (one row):
 *   [T] [title — fixed]    [C] [content — flex:1]    [×] [🔍]
 *
 * - `T` = title search (FTS5 on note_fts.title)
 * - `C` = content search (REGEXP, whitespace → AND)
 * - `×` = clear, `🔍` = search (accent blue, always last)
 */

export default function SearchBar({ onSearch }) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const titleRef = useRef(null);
  const contentRef = useRef(null);
  // IME composition guard: skip Enter while IME candidate window is open
  const composingRef = useRef(false);

  const active = title || content;

  const emit = useCallback((t, c) => {
    onSearch({ title: t.trim(), content: c.trim() });
  }, [onSearch]);

  const doSearch = () => {
    emit(title, content);
    // Blur to dismiss mobile keyboard
    document.activeElement?.blur();
  };

  const handleTitleKey = (e) => {
    if (composingRef.current) return;
    if (e.key === 'Enter') {
      e.preventDefault();
      doSearch();
    } else if (e.key === 'Escape') {
      setTitle(''); setContent('');
      emit('', '');
      titleRef.current?.blur();
    }
  };

  const handleContentKey = (e) => {
    if (composingRef.current) return;
    if (e.key === 'Enter') {
      e.preventDefault();
      doSearch();
    } else if (e.key === 'Escape') {
      setTitle(''); setContent('');
      emit('', '');
      contentRef.current?.blur();
    }
  };

  const handleClear = () => {
    setTitle(''); setContent('');
    emit('', '');
    titleRef.current?.focus();
  };

  return (
    <div className="search-bar">
      <label className="search-col search-col--title">
        <span className="search-col-icon" title="タイトル (FTS5)">T</span>
        <input
          ref={titleRef}
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onKeyDown={handleTitleKey}
          onCompositionStart={() => { composingRef.current = true; }}
          onCompositionEnd={() => { composingRef.current = false; }}
          placeholder="タイトル"
          className="search-input"
        />
      </label>

      <label className="search-col search-col--content">
        <span className="search-col-icon" title="本文 (正規表現)">C</span>
        <input
          ref={contentRef}
          type="text"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleContentKey}
          onCompositionStart={() => { composingRef.current = true; }}
          onCompositionEnd={() => { composingRef.current = false; }}
          placeholder="本文 (正規表現)"
          className="search-input"
        />
      </label>

      {/* clear button — visible when any field has content */}
      {active && (
        <button
          type="button"
          className="search-clear"
          onClick={handleClear}
          aria-label="検索をクリア"
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <circle cx="6" cy="6" r="5" fill="currentColor" opacity="0.2"/>
            <path d="M4 4L8 8M8 4L4 8" stroke="currentColor" strokeWidth="1.2"
              strokeLinecap="round"/>
          </svg>
        </button>
      )}

      {/* search button — accent, always last */}
      <button
        type="button"
        className="search-btn"
        onClick={doSearch}
        title="検索"
        aria-label="検索"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <circle cx="6.5" cy="6.5" r="5" stroke="currentColor" strokeWidth="1.5"/>
          <path d="M10.5 10.5L14.5 14.5" stroke="currentColor" strokeWidth="1.5"
            strokeLinecap="round"/>
        </svg>
      </button>
    </div>
  );
}
