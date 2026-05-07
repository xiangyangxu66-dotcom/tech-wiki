import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import NoteList from '../src/components/NoteList';

const notes = [
  {
    id: 1,
    title: 'Python入門',
    slug: 'python-intro',
    category_name: 'プログラミング',
    category_slug: 'programming',
    note_tags: ['Python', '入門'],
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 2,
    title: 'JavaScript入門',
    slug: 'javascript-intro',
    category_name: 'プログラミング',
    category_slug: 'programming',
    note_tags: ['JavaScript'],
    updated_at: '2026-01-02T00:00:00Z',
  },
];

describe('NoteList', () => {
  it('renders loading state', () => {
    render(<NoteList notes={[]} loading={true} />);
    expect(screen.getByText('読み込み中...')).toBeInTheDocument();
  });

  it('renders empty state when notes is empty array', () => {
    render(<NoteList notes={[]} loading={false} />);
    expect(screen.getByText('該当するノートがありません')).toBeInTheDocument();
  });

  it('renders empty state when notes is null', () => {
    render(<NoteList notes={null} loading={false} />);
    expect(screen.getByText('該当するノートがありません')).toBeInTheDocument();
  });

  it('renders note cards', () => {
    render(<NoteList notes={notes} loading={false} />);
    expect(screen.getAllByText('Python入門').length).toBeGreaterThan(0);
    expect(screen.getAllByText('JavaScript入門').length).toBeGreaterThan(0);
  });

  it('renders category name', () => {
    render(<NoteList notes={notes} loading={false} />);
    const categories = screen.getAllByText('プログラミング');
    expect(categories.length).toBeGreaterThanOrEqual(2);
  });

  it('renders tag badges', () => {
    render(<NoteList notes={notes} loading={false} />);
    expect(screen.getByText('Python')).toBeInTheDocument();
    expect(screen.getByText('入門')).toBeInTheDocument();
    expect(screen.getByText('JavaScript')).toBeInTheDocument();
  });

  it('renders links to note detail', () => {
    render(<NoteList notes={notes} loading={false} />);
    const link = screen.getAllByRole('link', { name: 'Python入門' })[0];
    expect(link).toHaveAttribute('href', '/note/python-intro/edit');
  });

  it('renders formatted date', () => {
    render(<NoteList notes={notes} loading={false} />);
    const dates = screen.getAllByText(/2026/);
    expect(dates.length).toBeGreaterThanOrEqual(2);
    const dateTexts = dates.map((node) => node.textContent);
    expect(dateTexts.some((text) => text?.includes('2026年1月2日'))).toBe(true);
    expect(dateTexts.some((text) => text?.includes('2026年1月1日'))).toBe(true);
  });

  it('paginates notes per tag by 10 items', async () => {
    const user = userEvent.setup();
    const many = Array.from({ length: 12 }, (_, i) => ({
      id: 100 + i,
      title: `Pythonノート${i + 1}`,
      slug: `python-note-${i + 1}`,
      category_name: 'プログラミング',
      note_tags: ['Python'],
      updated_at: '2026-01-03T00:00:00Z',
    }));

    render(<NoteList notes={many} loading={false} />);

    expect(screen.getByText('1 / 2')).toBeInTheDocument();
    expect(screen.getByText('Pythonノート1')).toBeInTheDocument();
    expect(screen.queryByText('Pythonノート11')).not.toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: '次へ' }));

    expect(screen.getByText('2 / 2')).toBeInTheDocument();
    expect(screen.getByText('Pythonノート11')).toBeInTheDocument();
  });
});
