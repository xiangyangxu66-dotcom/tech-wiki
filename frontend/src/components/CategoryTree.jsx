import { useState } from 'react';
import './CategoryTree.css';

function TreeNode({ node, level = 0, activeSlug, onSelect }) {
  const [expanded, setExpanded] = useState(level < 2);
  const hasChildren = node.children && node.children.length > 0;
  const isActive = activeSlug === node.slug;

  return (
    <li className="tree-node">
      <div
        className={`tree-item ${isActive ? 'active' : ''}`}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={() => {
          if (hasChildren) setExpanded(!expanded);
          onSelect(node.slug);
        }}
        role="treeitem"
        aria-expanded={hasChildren ? expanded : undefined}
        aria-selected={isActive}
      >
        {hasChildren ? (
          <svg
            className={`tree-chevron ${expanded ? 'expanded' : ''}`}
            width="12" height="12" viewBox="0 0 12 12" fill="none"
          >
            <path d="M4.5 2.5L8 6L4.5 9.5" stroke="currentColor" strokeWidth="1.5"
              strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        ) : (
          <span className="tree-chevron-placeholder" />
        )}
        <span className="tree-name">{node.name}</span>
        {node.note_count > 0 && (
          <span className="tree-count">{node.note_count}</span>
        )}
      </div>
      {hasChildren && expanded && (
        <ul className="tree-children" role="group">
          {node.children.map((child) => (
            <TreeNode
              key={child.id}
              node={child}
              level={level + 1}
              activeSlug={activeSlug}
              onSelect={onSelect}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

export default function CategoryTree({ categories, activeCategory, onSelectCategory }) {
  if (!categories || categories.length === 0) {
    return (
      <div className="category-tree-empty">
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none" className="empty-icon">
          <rect x="4" y="6" width="24" height="20" rx="3" stroke="currentColor" strokeWidth="1.5"/>
          <path d="M4 12h24" stroke="currentColor" strokeWidth="1.5"/>
        </svg>
        <p>カテゴリがありません</p>
      </div>
    );
  }

  return (
    <nav className="category-tree" role="tree">
      <div className="tree-section-label">カテゴリ</div>
      <ul className="tree-root">
        {categories.map((cat) => (
          <TreeNode
            key={cat.id}
            node={cat}
            activeSlug={activeCategory}
            onSelect={onSelectCategory}
          />
        ))}
      </ul>
    </nav>
  );
}
