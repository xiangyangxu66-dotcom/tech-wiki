import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import MarkdownRenderer from '../src/components/MarkdownRenderer';

vi.mock('../src/lib/highlight', () => ({
  default: {
    highlightElement: vi.fn(),
  },
}));

// Mock MermaidBlock to avoid lazy-load issues in jsdom
vi.mock('../src/components/MermaidBlock', () => ({
  default: ({ chart }) => `<div data-testid="mermaid">${chart}</div>`,
}));

describe('MarkdownRenderer — basic (existing)', () => {
  it('renders plain text', () => {
    render(<MarkdownRenderer content="Hello World" />);
    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });

  it('renders headings', () => {
    const md = '# 見出し1\n## 見出し2\n### 見出し3';
    render(<MarkdownRenderer content={md} />);
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('見出し1');
    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('見出し2');
    expect(screen.getByRole('heading', { level: 3 })).toHaveTextContent('見出し3');
  });

  it('renders inline code', () => {
    render(<MarkdownRenderer content="`console.log('hello')` を使ってください。" />);
    expect(screen.getByText("console.log('hello')")).toBeInTheDocument();
  });

  it('renders fenced code blocks', () => {
    const md = '```python\nprint("hello")\n```';
    render(<MarkdownRenderer content={md} />);
    expect(screen.getByText('print("hello")')).toBeInTheDocument();
  });

  it('renders links', () => {
    render(<MarkdownRenderer content="[Google](https://google.com)" />);
    const link = screen.getByRole('link');
    expect(link).toHaveTextContent('Google');
    expect(link).toHaveAttribute('href', 'https://google.com');
  });

  it('renders unordered lists', () => {
    const md = '- 項目1\n- 項目2';
    render(<MarkdownRenderer content={md} />);
    expect(screen.getAllByRole('listitem')).toHaveLength(2);
  });

  it('renders tables (gfm)', () => {
    const md = '| A | B |\n|---|---|\n| 1 | 2 |';
    render(<MarkdownRenderer content={md} />);
    expect(screen.getByRole('table')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('renders emphasis and strong', () => {
    render(<MarkdownRenderer content="*italic* **bold**" />);
    expect(screen.getByText('italic').tagName).toBe('EM');
    expect(screen.getByText('bold').tagName).toBe('STRONG');
  });

  it('wraps output in markdown-body class', () => {
    const { container } = render(<MarkdownRenderer content="test" />);
    expect(container.querySelector('.markdown-body')).toBeInTheDocument();
  });
});

describe('MarkdownRenderer — GFM extensions', () => {
  it('renders strikethrough', () => {
    render(<MarkdownRenderer content="~~deleted~~ text" />);
    const del = screen.getByText('deleted');
    expect(del.tagName).toBe('DEL');
  });

  it('renders task list items', () => {
    const md = '- [x] Done\n- [ ] Todo';
    render(<MarkdownRenderer content={md} />);
    const items = screen.getAllByRole('listitem');
    expect(items).toHaveLength(2);
    // Task lists have checkbox inputs
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    expect(checkboxes).toHaveLength(2);
  });

  it('renders blockquotes', () => {
    render(<MarkdownRenderer content="> quoted text" />);
    const blockquote = document.querySelector('blockquote');
    expect(blockquote).toBeTruthy();
    expect(blockquote.textContent).toContain('quoted text');
  });

  it('renders ordered lists', () => {
    const md = '1. first\n2. second';
    render(<MarkdownRenderer content={md} />);
    const items = screen.getAllByRole('listitem');
    expect(items).toHaveLength(2);
    expect(items[0].textContent).toContain('first');
  });
});

describe('MarkdownRenderer — code blocks (edge cases)', () => {
  it('renders fenced code without language', () => {
    const md = '```\nno lang code\n```';
    render(<MarkdownRenderer content={md} />);
    expect(screen.getByText('no lang code')).toBeInTheDocument();
  });

  it('renders mermaid code with enableMermaid=true', () => {
    const md = '```mermaid\ngraph TD; A-->B;\n```';
    const { container } = render(<MarkdownRenderer content={md} enableMermaid={true} />);
    // Suspense wraps it; the mock returns a div with data-testid
    // Since we mock MermaidBlock, the code string appears somewhere
    expect(container.textContent).toContain('graph TD');
  });

  it('falls back to plain code when enableMermaid=false', () => {
    const md = '```mermaid\ngraph TD; A-->B;\n```';
    render(<MarkdownRenderer content={md} enableMermaid={false} />);
    // Should render as regular code block, not mermaid
    expect(screen.getByText('graph TD; A-->B;')).toBeInTheDocument();
  });
});

describe('MarkdownRenderer — edge cases', () => {
  it('renders empty string content', () => {
    const { container } = render(<MarkdownRenderer content="" />);
    expect(container.querySelector('.markdown-body')).toBeTruthy();
  });

  it('renders null/undefined content gracefully', () => {
    // react-markdown will just render nothing for null/undefined
    const { container } = render(<MarkdownRenderer content={null} />);
    expect(container.querySelector('.markdown-body')).toBeTruthy();
  });

  it('renders horizontal rule', () => {
    render(<MarkdownRenderer content="---" />);
    expect(document.querySelector('hr')).toBeTruthy();
  });

  it('renders images', () => {
    render(<MarkdownRenderer content="![alt](https://img.com/pic.png)" />);
    const img = screen.getByAltText('alt');
    expect(img).toBeTruthy();
    expect(img.getAttribute('src')).toBe('https://img.com/pic.png');
  });

  it('renders nested formatting', () => {
    render(<MarkdownRenderer content="**bold and *italic* combo**" />);
    const strong = screen.getByText(/bold and/);
    expect(strong.tagName).toBe('STRONG');
    const em = strong.querySelector('em');
    expect(em).toBeTruthy();
    expect(em.textContent).toBe('italic');
  });
});
