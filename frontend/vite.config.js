import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [
    react(),
    // note detail route.
    {
      name: 'mpa-routes',
      configureServer(server) {
        server.middlewares.use((req, _res, next) => {
          if (req.url?.startsWith('/note/') && !req.url.includes('.')) {
            req.url = '/note.html';
          }
          next();
        });
      },
    },
  ],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    // Mermaid vendor chunk is intentionally large but route/lazy loaded.
    // Raise warning threshold to avoid noisy false-positive warnings in this architecture.
    chunkSizeWarningLimit: 2300,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        note: resolve(__dirname, 'note.html'),
      },
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return;

          if (id.includes('/node_modules/react/') || id.includes('/node_modules/react-dom/')) {
            return 'vendor-react';
          }

          if (
            id.includes('/node_modules/cytoscape/') ||
            id.includes('/node_modules/cose-base/') ||
            id.includes('/node_modules/cytoscape-cose-bilkent/') ||
            id.includes('/node_modules/layout-base/')
          ) {
            return 'vendor-mermaid-cytoscape';
          }

          if (id.includes('/node_modules/mermaid/')) {
            return 'vendor-mermaid';
          }

          if (
            id.includes('/node_modules/react-markdown/') ||
            id.includes('/node_modules/remark-gfm/') ||
            id.includes('/node_modules/remark-') ||
            id.includes('/node_modules/rehype-') ||
            id.includes('/node_modules/unified/') ||
            id.includes('/node_modules/mdast-') ||
            id.includes('/node_modules/micromark/')
          ) {
            return 'vendor-markdown';
          }

          if (id.includes('/node_modules/highlight.js/')) {
            return 'vendor-highlight';
          }

          if (id.includes('/node_modules/katex/')) {
            return 'vendor-katex';
          }
        },
      },
    },
  },
});
