import React, { Suspense, lazy } from 'react';
import ReactDOM from 'react-dom/client';
import { resolveNoteRoute } from './noteRoute';
import './index.css';

const NotePage = lazy(() => import('./NotePage'));
const NoteEditorPage = lazy(() => import('./NoteEditorPage'));

const { isEdit, slug } = resolveNoteRoute(window.location);

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <Suspense fallback={<div className="editor-shell-state">読み込み中...</div>}>
            {isEdit ? <NoteEditorPage slug={slug} /> : <NotePage slug={slug} />}
        </Suspense>
    </React.StrictMode>
);
