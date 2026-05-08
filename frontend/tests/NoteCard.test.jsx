import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import NoteCard from '../src/components/NoteCard.jsx';

const baseNote = {
  slug: 'react-guide',
  title: 'Reactガイド',
  content: '# React\nReactはUIライブラリです。',
  note_tags: ['React', 'JavaScript'],
  bookmark: false,
  category_name: '',
  status: 'published',
  updated_at: '2026-01-15T10:30:00Z',
};

describe('NoteCard — list mode (default)', () => {
  it('renders title and icon', () => {
    render(<NoteCard note={baseNote} />);
    expect(screen.getByText('Reactガイド')).toBeTruthy();
    // tag-based icon
    expect(screen.getByText('⚛️')).toBeTruthy();
  });

  it('renders category when category_name is set', () => {
    const note = { ...baseNote, category_name: 'Frontend' };
    render(<NoteCard note={note} />);
    expect(screen.getByText('Frontend')).toBeTruthy();
  });

  it('shows draft badge when status is draft', () => {
    const note = { ...baseNote, status: 'draft' };
    render(<NoteCard note={note} />);
    expect(screen.getByText('下書き')).toBeTruthy();
  });

  it('does not show draft badge when status is published', () => {
    render(<NoteCard note={baseNote} />);
    expect(screen.queryByText('下書き')).toBeNull();
  });

  it('renders formatted date', () => {
    render(<NoteCard note={baseNote} />);
    // Locale 'ja-JP' with 'numeric'/'short'/'numeric' → something like "2026/1/15"
    expect(screen.getByText(/2026/)).toBeTruthy();
  });

  it('shows empty date when updated_at is null', () => {
    const note = { ...baseNote, updated_at: null };
    const { container } = render(<NoteCard note={note} />);
    // empty date span should still be there but with empty text
    const dateSpan = container.querySelector('.card-date');
    expect(dateSpan.textContent).toBe('');
  });

  it('renders search snippet with dangerouslySetInnerHTML', () => {
    const note = { ...baseNote, _snippet: 'Reactは<mark>UI</mark>ライブラリです。' };
    const { container } = render(<NoteCard note={note} />);
    const snippet = container.querySelector('.card-snippet');
    expect(snippet).toBeTruthy();
    expect(snippet.innerHTML).toContain('<mark>UI</mark>');
  });

  it('does not render snippet div when _snippet is absent', () => {
    const { container } = render(<NoteCard note={baseNote} />);
    expect(container.querySelector('.card-snippet')).toBeNull();
  });

  it('StarIcon shows unfilled for non-bookmarked note', () => {
    render(<NoteCard note={baseNote} />);
    const btn = screen.getByLabelText('ブックマークする');
    expect(btn).toBeTruthy();
  });

  it('StarIcon shows filled for bookmarked note', () => {
    const note = { ...baseNote, bookmark: true };
    render(<NoteCard note={note} />);
    expect(screen.getByLabelText('ブックマークを外す')).toBeTruthy();
  });

  it('onBookmarkToggle callback receives slug on star click', () => {
    const toggleFn = vi.fn();
    const note = { ...baseNote, bookmark: false };
    render(<NoteCard note={note} onBookmarkToggle={toggleFn} />);
    fireEvent.click(screen.getByLabelText('ブックマークする'));
    expect(toggleFn).toHaveBeenCalledWith('react-guide');
  });

  it('does not throw when onBookmarkToggle is not provided', () => {
    render(<NoteCard note={baseNote} />);
    // click without onBookmarkToggle — no error
    fireEvent.click(screen.getByLabelText('ブックマークする'));
  });
});

describe('NoteCard — icon mode', () => {
  it('renders icon-mode layout', () => {
    const { container } = render(<NoteCard note={baseNote} mode="icon" />);
    expect(container.querySelector('.card-icon')).toBeTruthy();
    expect(container.querySelector('.card-icon-symbol')).toBeTruthy();
    expect(container.querySelector('.card-icon-title')).toBeTruthy();
  });

  it('shows bookmark button in icon mode', () => {
    const note = { ...baseNote, bookmark: true };
    render(<NoteCard note={note} mode="icon" />);
    expect(screen.getByLabelText('ブックマークを外す')).toBeTruthy();
  });
});

describe('NoteCard — icon selection (pickIcon)', () => {
  it('picks icon from matching tag', () => {
    const note = { ...baseNote, note_tags: ['Python'], title: 'Some Guide' };
    render(<NoteCard note={note} />);
    expect(screen.getByText('🐍')).toBeTruthy();
  });

  it('falls back to title match when no tag matches', () => {
    const note = { ...baseNote, note_tags: [], title: 'Django入門' };
    render(<NoteCard note={note} />);
    expect(screen.getByText('🧩')).toBeTruthy();
  });

  it('returns default 📄 when nothing matches', () => {
    const note = { ...baseNote, note_tags: ['UnknownTag'], title: 'Random' };
    render(<NoteCard note={note} />);
    expect(screen.getByText('📄')).toBeTruthy();
  });

  it('handles null/undefined tags gracefully', () => {
    const note = { ...baseNote, note_tags: null };
    render(<NoteCard note={note} />);
    // should not crash — falls back to title match or default
    expect(screen.getByText('Reactガイド')).toBeTruthy();
  });
});

describe('NoteCard — link targets', () => {
  it('card links to edit page', () => {
    render(<NoteCard note={baseNote} />);
    const links = screen.getAllByRole('link');
    const hrefs = links.map(l => l.getAttribute('href'));
    expect(hrefs).toContain('/note/react-guide/edit');
  });

  it('icon mode also links to edit page', () => {
    render(<NoteCard note={baseNote} mode="icon" />);
    const link = screen.getByRole('link');
    expect(link.getAttribute('href')).toBe('/note/react-guide/edit');
  });
});

describe('NoteCard — search term highlighting', () => {
  it('highlights title when searchTerms match', () => {
    const { container } = render(
      <NoteCard note={baseNote} searchTerms={['React']} />
    );
    const marks = container.querySelectorAll('.card-title mark');
    expect(marks.length).toBe(1);
    expect(marks[0].textContent).toBe('React');
  });

  it('highlights multiple match occurrences', () => {
    const note = { ...baseNote, title: 'ReactとReactNative' };
    const { container } = render(
      <NoteCard note={note} searchTerms={['React']} />
    );
    const marks = container.querySelectorAll('.card-title mark');
    expect(marks.length).toBe(2);
  });

  it('highlights in icon mode title', () => {
    const { container } = render(
      <NoteCard note={baseNote} mode="icon" searchTerms={['React']} />
    );
    const marks = container.querySelectorAll('.card-icon-title mark');
    expect(marks.length).toBe(1);
  });

  it('does not highlight when searchTerms is empty', () => {
    const { container } = render(
      <NoteCard note={baseNote} searchTerms={[]} />
    );
    expect(container.querySelector('.card-title mark')).toBeNull();
  });

  it('does not highlight when searchTerms is undefined', () => {
    const { container } = render(<NoteCard note={baseNote} />);
    expect(container.querySelector('.card-title mark')).toBeNull();
  });

  it('escapes regex special characters in search terms', () => {
    const note = { ...baseNote, title: 'C++ガイド' };
    const { container } = render(
      <NoteCard note={note} searchTerms={['C++']} />
    );
    const marks = container.querySelectorAll('.card-title mark');
    expect(marks.length).toBe(1);
    expect(marks[0].textContent).toBe('C++');
  });

  it('highlights with case-insensitive matching', () => {
    const note = { ...baseNote, title: 'REACTガイド' };
    const { container } = render(
      <NoteCard note={note} searchTerms={['react']} />
    );
    const marks = container.querySelectorAll('.card-title mark');
    expect(marks.length).toBe(1);
    expect(marks[0].textContent).toBe('REACT');
  });

  it('highlights multiple distinct terms', () => {
    const note = { ...baseNote, title: 'ReactとJavaScriptガイド' };
    const { container } = render(
      <NoteCard note={note} searchTerms={['React', 'JavaScript']} />
    );
    const marks = container.querySelectorAll('.card-title mark');
    expect(marks.length).toBe(2);
  });
});
