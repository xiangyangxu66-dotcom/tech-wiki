import { useEffect, useState, useCallback } from 'react';
import { fetchTags } from '../api/notes';
import './TagTree.css';

/**
 * TagTree — タグ動的グループによるサイドバーナビ
 * tags: [{name: string, count: number}, ...]
 */
const SORT_MODES = [
  { value: 'updated', label: '更新順' },
  { value: 'alpha', label: 'ABC' },
  { value: 'count', label: '件数順' },
];

export default function TagTree({ activeTag, onTagSelect }) {
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sort, setSort] = useState(() => {
    try { return localStorage.getItem('techwiki:tagSort') || 'updated'; }
    catch { return 'updated'; }
  });

  const loadTags = useCallback((sortMode) => {
    setLoading(true);
    fetchTags({ sort: sortMode })
      .then(data => { setTags(data); setError(null); })
      .catch(e => { console.error('TagTree fetch error', e); setError(e.message); })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    loadTags(sort);
  }, [sort, loadTags]);

  const handleSortChange = (mode) => {
    setSort(mode);
    try { localStorage.setItem('techwiki:tagSort', mode); } catch {}
  };

  return (
    <div className="tag-tree-section">
      {/* 全件表示 */}
      <div className={`tag-tree-item ${!activeTag ? 'active' : ''}`}>
        <button onClick={() => onTagSelect(null)}>
          <span className="tag-tree-icon all" aria-hidden="true">◇</span>
          <span className="tag-tree-label">技術Memo</span>
        </button>
      </div>

      <div className="tag-tree-divider" />

      {/* タグ一覧ヘッダー + ソート選択 */}
      <div className="tag-tree-header-row">
        <div className="tag-tree-label-header">タグ</div>
        <select
          className="sort-select tag-sort-select"
          value={sort}
          onChange={(event) => handleSortChange(event.target.value)}
          aria-label="タグの並び順"
        >
          {SORT_MODES.map(m => (
            <option key={m.value} value={m.value}>{m.label}</option>
          ))}
        </select>
      </div>

      {loading && <div className="tag-tree-loading">読み込み中...</div>}
      {error && <div className="tag-tree-error">タグ取得失敗</div>}

      {!loading && !error && tags.map(tag => {
        const isUntagged = tag.name === '無所属';
        return (
          <div
            key={tag.name}
            className={`tag-tree-item ${activeTag === tag.name ? 'active' : ''} ${isUntagged ? 'untagged' : ''}`}
          >
            <button onClick={() => onTagSelect(tag.name === activeTag ? null : tag.name)}>
              <span className={`tag-tree-icon ${isUntagged ? 'untagged-icon' : 'tag-icon'}`} aria-hidden="true">
                {isUntagged ? '○' : '#'}
              </span>
              <span className="tag-tree-label">{tag.name}</span>
              <span className="tag-tree-badge">{tag.count}</span>
            </button>
          </div>
        );
      })}

      {!loading && !error && tags.length === 0 && (
        <div className="tag-tree-empty">タグがありません</div>
      )}
    </div>
  );
}
