import { Suspense, lazy, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import hljs from '../lib/highlight';
import './MarkdownRenderer.css';
import 'highlight.js/styles/github.css';

const MermaidBlock = lazy(() => import('./MermaidBlock'));

export default function MarkdownRenderer({ content, enableMermaid = true }) {
  useEffect(() => {
    document.querySelectorAll('.markdown-body pre code').forEach((block) => {
      hljs.highlightElement(block);
    });
  }, [content]);

  return (
    <div className="markdown-body">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const codeStr = String(children).replace(/\n$/, '');

            if (!inline && match && match[1] === 'mermaid' && enableMermaid) {
              return (
                <Suspense fallback={<pre><code>{codeStr}</code></pre>}>
                  <MermaidBlock chart={codeStr} />
                </Suspense>
              );
            }

            if (!inline && match) {
              return (
                <pre className={className}>
                  <code className={className} {...props}>
                    {codeStr}
                  </code>
                </pre>
              );
            }

            return (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
