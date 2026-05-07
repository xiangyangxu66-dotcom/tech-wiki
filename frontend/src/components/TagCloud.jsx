import './TagCloud.css';

export default function TagCloud({ tags, activeTag, onTagClick }) {
  // tags: [['入門', 3], ['チートシート', 2], ...]
  if (!tags || tags.length === 0) return null;

  return (
    <div className="tag-cloud">
      {tags.map(([name, count]) => (
        <button
          key={name}
          className={`tag-chip ${name === activeTag ? 'active' : ''}`}
          onClick={() => onTagClick(name)}
          title={`${name} (${count}件)`}
        >
          {name}
          <span className="tag-count">{count}</span>
        </button>
      ))}
    </div>
  );
}
