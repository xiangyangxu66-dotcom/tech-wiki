import { useEffect, useRef } from 'react';

let mermaidInstancePromise;

function getMermaid() {
  if (!mermaidInstancePromise) {
    mermaidInstancePromise = import('mermaid').then(({ default: mermaid }) => {
      mermaid.initialize({
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose',
      });
      return mermaid;
    });
  }
  return mermaidInstancePromise;
}

export default function MermaidBlock({ chart }) {
  const ref = useRef(null);
  const idRef = useRef(`mermaid-${Math.random().toString(36).slice(2, 9)}`);

  useEffect(() => {
    let cancelled = false;

    async function renderChart() {
      if (!ref.current) return;
      try {
        const mermaid = await getMermaid();
        const { svg } = await mermaid.render(idRef.current, chart);
        if (!cancelled && ref.current) {
          ref.current.innerHTML = svg;
        }
      } catch (err) {
        if (!cancelled && ref.current) {
          ref.current.innerHTML = `<pre class="mermaid-error">Mermaid render error: ${err.message}</pre>`;
        }
      }
    }

    void renderChart();
    return () => {
      cancelled = true;
    };
  }, [chart]);

  return <div ref={ref} className="mermaid-block" />;
}
