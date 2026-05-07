import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import CategoryTree from '../src/components/CategoryTree';

const flatCategories = [
  {
    id: 1,
    name: 'プログラミング',
    slug: 'programming',
    note_count: 5,
    parent: null,
    children: [],
  },
];

const treeCategories = [
  {
    id: 1,
    name: '技術',
    slug: 'tech',
    note_count: 10,
    parent: null,
    children: [
      {
        id: 2,
        name: '言語',
        slug: 'lang',
        note_count: 5,
        parent: 1,
        children: [
          { id: 3, name: 'Python', slug: 'python', note_count: 3, parent: 2, children: [] },
          { id: 4, name: 'JavaScript', slug: 'javascript', note_count: 2, parent: 2, children: [] },
        ],
      },
      {
        id: 5,
        name: 'インフラ',
        slug: 'infra',
        note_count: 3,
        parent: 1,
        children: [],
      },
    ],
  },
];

describe('CategoryTree', () => {
  it('renders empty state when no categories', () => {
    render(<CategoryTree categories={[]} />);
    expect(screen.getByText('カテゴリがありません')).toBeInTheDocument();
  });

  it('handles null/undefined categories gracefully', () => {
    render(<CategoryTree categories={null} />);
    // null → empty check, should render empty message
    expect(screen.getByText('カテゴリがありません')).toBeInTheDocument();
  });

  it('renders flat category list', () => {
    render(<CategoryTree categories={flatCategories} />);
    expect(screen.getByText('プログラミング')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('renders tree structure', () => {
    render(<CategoryTree categories={treeCategories} />);
    // Root level
    expect(screen.getByText('技術')).toBeInTheDocument();
    // Level 1 children (expanded by default for level < 2)
    expect(screen.getByText('言語')).toBeInTheDocument();
    expect(screen.getByText('インフラ')).toBeInTheDocument();
    // Level 2 children (also expanded)
    expect(screen.getByText('Python')).toBeInTheDocument();
    expect(screen.getByText('JavaScript')).toBeInTheDocument();
  });

  it('calls onSelectCategory when a category is clicked', async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    render(<CategoryTree categories={flatCategories} onSelectCategory={onSelect} />);
    await user.click(screen.getByText('プログラミング'));
    expect(onSelect).toHaveBeenCalledWith('programming');
  });

  it('toggles expand/collapse on folder click', async () => {
    const user = userEvent.setup();
    // Use a tree where level 2 nodes are NOT auto-expanded (level >= 2)
    const deepTree = [
      {
        id: 1,
        name: 'Top',
        slug: 'top',
        note_count: 1,
        parent: null,
        children: [
          {
            id: 2,
            name: 'Mid',
            slug: 'mid',
            note_count: 1,
            parent: 1,
            children: [
              { id: 3, name: 'Deep', slug: 'deep', note_count: 1, parent: 2, children: [] },
            ],
          },
        ],
      },
    ];
    render(<CategoryTree categories={deepTree} />);
    // Top and Mid are auto-expanded (level 0 and 1 < 2)
    expect(screen.getByText('Deep')).toBeInTheDocument();
  });

  it('applies active class to the selected category', () => {
    render(<CategoryTree categories={flatCategories} activeCategory="programming" />);
    const item = screen.getByText('プログラミング').closest('.tree-item');
    expect(item).toHaveClass('active');
  });
});
