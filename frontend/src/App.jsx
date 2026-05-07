import { useState, useEffect, useCallback } from 'react';
import { fetchNotes } from './api/notes';
import TagTree from './components/TagTree';
import NoteList from './components/NoteList';
import SearchBar from './components/SearchBar';
import HealthIndicator from './components/HealthIndicator';
import './App.css';

function useNotes(activeTag, searchParams) {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const load = useCallback(() => {
    setLoading(true);
    const params = {};
    if (activeTag) params.tag = activeTag;
    if (searchParams?.title) params.search_title = searchParams.title;
    if (searchParams?.content) {
      params.search_content = searchParams.content;
    }
    fetchNotes(params)
      .then(data => { setNotes(data.results || data); setError(null); })
      .catch(e => { setError(e.message); setNotes([]); })
      .finally(() => setLoading(false));
  }, [activeTag, searchParams]);

  useEffect(() => { load(); }, [load]);
  return { notes, loading, error, refresh: load, setNotes };
}

export default function App() {
  const [activeTag, setActiveTag] = useState(null);
  const [searchParams, setSearchParams] = useState({});
  const { notes, loading, error, setNotes } = useNotes(activeTag, searchParams);

  useEffect(() => {
    const onKeyDown = (event) => {
      const target = event.target;
      const isEditable = target instanceof HTMLElement
        && (target.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName));

      if (isEditable) return;

      if (!event.metaKey && !event.ctrlKey && !event.altKey && event.key.toLowerCase() === 'n') {
        event.preventDefault();
        window.location.href = '/note/new/edit';
      }
    };

    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  return (
    <div className="app-layout">
      {/* ── サイドバー ── */}
      <aside className="sidebar">
        <div className="sidebar-scroll">
          <TagTree
            activeTag={activeTag}
            onTagSelect={setActiveTag}
          />
        </div>

        <div className="sidebar-footer">
          <HealthIndicator />
        </div>
      </aside>

      {/* ── メインコンテンツ ── */}
      <main className="main-content">
        <div className="main-header">
          <div className="main-header-top">
            <div className="window-chrome" aria-hidden="true">
              <span className="dot dot-red" />
              <span className="dot dot-yellow" />
              <span className="dot dot-green" />
            </div>
          </div>
          <h1>Tech-Wiki</h1>
          <p className="main-subtitle">技術知識の集積と再構成</p>
          <p className="main-shortcuts">Shortcut: N で新規ノート</p>
          {activeTag && (
            <div className="active-filter">
              <span className="filter-column">tag</span>
              <span className="filter-op">:</span>
              <span className="filter-value">{activeTag}</span>
              <button className="filter-clear" onClick={() => setActiveTag(null)}>✕</button>
            </div>
          )}
        </div>

        <div className="main-body">
          <div className="search-row">
            <SearchBar onSearch={setSearchParams} />
          </div>
          <NoteList
            notes={notes}
            loading={loading}
            activeTag={activeTag}
            onTagClick={tag => setActiveTag(tag === activeTag ? null : tag)}
            onNotesChange={setNotes}
          />
          <footer className="main-footer" />
        </div>
      </main>
    </div>
  );
}
