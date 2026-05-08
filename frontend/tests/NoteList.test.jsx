import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import NoteList from '../src/components/NoteList';

// Mock notes.js toggleBookmark so we don't make real API calls
vi.mock('../src/api/notes', () => ({
  toggleBookmark: vi.fn().mockResolvedValue({}),
}));

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

describe('NoteList — basic rendering (existing)', () => {
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

  it('renders tag groups as section dividers', () => {
    render(<NoteList notes={notes} loading={false} />);
    // #Python, #JavaScript, #入門 appear as section dividers
    expect(screen.getByText('Python')).toBeInTheDocument();
    expect(screen.getByText('JavaScript')).toBeInTheDocument();
    expect(screen.getByText('入門')).toBeInTheDocument();
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

describe('NoteList — view mode & column toggle', () => {
  it('toggles between list and icon mode', async () => {
    const user = userEvent.setup();
    render(<NoteList notes={notes} loading={false} />);
    // default is list mode
    const listBtn = screen.getByTitle('リスト表示');
    const iconBtn = screen.getByTitle('アイコン表示');
    expect(listBtn.classList.contains('active')).toBe(true);
    expect(iconBtn.classList.contains('active')).toBe(false);

    await user.click(iconBtn);
    expect(iconBtn.classList.contains('active')).toBe(true);
    expect(listBtn.classList.contains('active')).toBe(false);

    await user.click(listBtn);
    expect(listBtn.classList.contains('active')).toBe(true);
    expect(iconBtn.classList.contains('active')).toBe(false);
  });

  it('shows column toggle only in list mode', () => {
    const { container } = render(<NoteList notes={notes} loading={false} />);
    // list mode → column toggle visible
    expect(screen.getByText('2列')).toBeTruthy();
    expect(screen.getByText('3列')).toBeTruthy();
    expect(screen.getByText('4列')).toBeTruthy();
  });

  it('switches column count', async () => {
    const user = userEvent.setup();
    const { container } = render(<NoteList notes={notes} loading={false} />);
    const btn2 = screen.getByText('2列');
    const btn4 = screen.getByText('4列');
    expect(btn2.classList.contains('active')).toBe(false);
    expect(btn4.classList.contains('active')).toBe(false);
    // default is 3
    expect(screen.getByText('3列').classList.contains('active')).toBe(true);

    await user.click(btn2);
    expect(btn2.classList.contains('active')).toBe(true);

    await user.click(btn4);
    expect(btn4.classList.contains('active')).toBe(true);
  });
});

describe('NoteList — sort', () => {
  it('renders sort select with all options', () => {
    render(<NoteList notes={notes} loading={false} />);
    expect(screen.getByText('更新日時')).toBeTruthy();
    expect(screen.getByText('作成日時')).toBeTruthy();
    expect(screen.getByText('ファイル名')).toBeTruthy();
  });

  it('changes sort key on select', async () => {
    const user = userEvent.setup();
    render(<NoteList notes={notes} loading={false} />);
    const select = screen.getByRole('combobox');
    await user.selectOptions(select, 'title');
    expect(select.value).toBe('title');
  });
});

describe('NoteList — bookmarks', () => {
  it('renders bookmark section when bookmarked notes exist', () => {
    const noteWithBookmark = [
      { ...notes[0], bookmark: true },
      notes[1],
    ];
    render(<NoteList notes={noteWithBookmark} loading={false} />);
    expect(screen.getByText('ピン留め')).toBeTruthy();
    expect(screen.getByText('📌')).toBeTruthy();
  });

  it('does not render bookmark section when no bookmarks', () => {
    render(<NoteList notes={notes} loading={false} />);
    expect(screen.queryByText('ピン留め')).toBeNull();
  });

  it('calls toggleBookmark and optimistically updates', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<NoteList notes={notes} loading={false} onNotesChange={onChange} />);
    const starBtn = screen.getAllByLabelText('ブックマークする')[0];
    await user.click(starBtn);
    expect(onChange).toHaveBeenCalled();
  });
});

describe('NoteList — untagged notes', () => {
  it('groups notes with no tags under 未分類タグ', () => {
    const untagged = [
      { id: 9, title: 'タグなし', slug: 'no-tag', note_tags: [], updated_at: '2026-01-01T00:00:00Z' },
    ];
    render(<NoteList notes={untagged} loading={false} />);
    // The section divider text includes '未分類タグ'
    const sections = screen.getAllByText(/未分類タグ/);
    expect(sections.length).toBeGreaterThan(0);
  });
});

describe('NoteList — exactly 10 items (no pagination)', () => {
  it('shows no pagination when exactly 10 items per tag', () => {
    const ten = Array.from({ length: 10 }, (_, i) => ({
      id: 200 + i,
      title: `Goノート${i + 1}`,
      slug: `go-note-${i + 1}`,
      note_tags: ['Go'],
      updated_at: '2026-01-01T00:00:00Z',
    }));
    render(<NoteList notes={ten} loading={false} />);
    expect(screen.queryByText('前へ')).toBeNull();
    expect(screen.queryByText('次へ')).toBeNull();
  });
});

describe('NoteList — toolbar', () => {
  it('renders Note作成 link', () => {
    render(<NoteList notes={notes} loading={false} />);
    const link = screen.getByText('Note作成');
    expect(link.getAttribute('href')).toBe('/note/new/edit');
  });
});
