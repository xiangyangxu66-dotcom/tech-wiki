import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import MarkdownRenderer from '../src/components/MarkdownRenderer';

// highlight.js は jsdom 環境で DOM がないとエラーになるのでモック
vi.mock('../src/lib/highlight', () => ({
  default: {
    highlightElement: vi.fn(),
  },
}));

describe('MarkdownRenderer', () => {
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
