import { Suspense, lazy, useCallback, useEffect, useMemo, useState } from 'react';
import { createNote, deleteNote, fetchNote, updateNote } from './api/notes';
import './NoteEditorPage.css';

const MarkdownRenderer = lazy(() => import('./components/MarkdownRenderer'));

const EMPTY_NOTE = { title: '', content: '' };

export default function NoteEditorPage({ slug }) {
    const isNew = !slug;
    const [note, setNote] = useState(EMPTY_NOTE);
    const [savedNote, setSavedNote] = useState(EMPTY_NOTE); // 最後に保存したスナップショット
    const [loading, setLoading] = useState(!isNew);
    const [saving, setSaving] = useState(false);
    const [deleting, setDeleting] = useState(false);
    const [error, setError] = useState(null);

    // ── Load existing note ──
    useEffect(() => {
        let cancelled = false;

        if (isNew) {
            setLoading(false);
            return () => { cancelled = true; };
        }

        fetchNote(slug)
            .then((data) => {
                if (!cancelled) {
                    const loaded = { title: data.title || '', content: data.content || '' };
                    setNote(loaded);
                    setSavedNote(loaded);
                }
            })
            .catch((err) => {
                if (!cancelled) {
                    console.error(err);
                    setError('ノートの読み込みに失敗しました');
                }
            })
            .finally(() => { if (!cancelled) setLoading(false); });

        return () => { cancelled = true; };
    }, [isNew, slug]);

    const previewTitle = note.title.trim() || 'Untitled';

    const handleFieldChange = (field, value) => {
        setNote((current) => ({ ...current, [field]: value }));
    };

    // 未保存変更があるか（新規は空でなければ dirty）
    const dirty = useMemo(() => {
        if (isNew) return note.title.trim() !== '' || note.content.trim() !== '';
        return note.title !== savedNote.title || note.content !== savedNote.content;
    }, [isNew, note.title, note.content, savedNote]);

    // ── 一覧に戻る（未保存があれば確認）──
    const handleGoBack = (e) => {
        if (dirty) {
            const ok = window.confirm('未保存の変更があります。破棄して一覧に戻りますか？');
            if (!ok) { e.preventDefault(); return; }
        }
        window.location.href = '/';
    };

    // ── Save ──
    const handleSave = useCallback(async () => {
        if (!note.title.trim()) {
            setError('タイトルを入力してください');
            return;
        }
        setSaving(true);
        setError(null);
        try {
            const payload = { title: note.title.trim(), content: note.content };
            const saved = isNew ? await createNote(payload) : await updateNote(slug, payload);
            if (isNew && saved.slug) {
                window.location.href = `/note/${saved.slug}/edit`;
                return;
            }
            // 更新成功 → dirty クリア
            if (!isNew) setSavedNote(payload);
        } catch (err) {
            console.error(err);
            setError(err.message || '保存に失敗しました');
        } finally {
            setSaving(false);
        }
    }, [isNew, note.content, note.title, slug]);

    // ── Keyboard shortcuts ──
    useEffect(() => {
        const onKeyDown = (event) => {
            if ((event.metaKey || event.ctrlKey) && event.key === 's') {
                event.preventDefault();
                void handleSave();
            }
        };
        window.addEventListener('keydown', onKeyDown);
        return () => window.removeEventListener('keydown', onKeyDown);
    }, [handleSave]);

    // ── Delete ──
    async function handleDelete() {
        if (isNew) {
            window.location.href = '/';
            return;
        }
        const confirmed = window.confirm(`「${note.title || slug}」を削除しますか？`);
        if (!confirmed) return;
        setDeleting(true);
        setError(null);
        try {
            await deleteNote(slug);
            window.location.href = '/';
        } catch (err) {
            console.error(err);
            setError(err.message || '削除に失敗しました');
        } finally {
            setDeleting(false);
        }
    }

    // ── Loading ──
    if (loading) {
        return <div className="editor-shell-state">読み込み中...</div>;
    }

    return (
        <div className="editor-shell">
            {/* ── Top bar ── */}
            <header className="editor-topbar">
                <div className="editor-topbar-left">
                    <a href="/" className="editor-nav-link" onClick={handleGoBack}>一覧に戻る</a>
                    <span className="editor-shortcuts">⌘S 保存</span>
                </div>
                <div className="editor-topbar-right">
                    {!isNew && (
                        <button
                            type="button"
                            className="editor-danger-btn"
                            onClick={handleDelete}
                            disabled={deleting}
                        >
                            {deleting ? '削除中...' : '削除'}
                        </button>
                    )}
                    <button
                        type="button"
                        className="editor-primary-btn"
                        onClick={() => { void handleSave(); }}
                        disabled={saving}
                    >
                        {isNew
                            ? (saving ? '作成中...' : '作成')
                            : (saving ? '保存中...' : '保存')}
                    </button>
                </div>
            </header>

            {/* ── Error banner ── */}
            {error && <div className="editor-error-banner">{error}</div>}

            {/* ── Split pane: Write | Preview ── */}
            <div className="editor-grid">
                <section className="editor-pane editor-pane-write">
                    <div className="editor-pane-header">Write</div>
                    <div className="editor-form-row">
                        <input
                            className="editor-title-input"
                            value={note.title}
                            onChange={(e) => handleFieldChange('title', e.target.value)}
                            placeholder="Note title"
                        />
                    </div>
                    <textarea
                        className="editor-textarea"
                        value={note.content}
                        onChange={(e) => handleFieldChange('content', e.target.value)}
                        placeholder={'# Start writing\n\nHackMD 風に Markdown を編集できます。'}
                    />
                </section>

                <section className="editor-pane editor-pane-preview">
                    <div className="editor-pane-header">Preview</div>
                    <div className="editor-preview-head">
                        <h1>{previewTitle}</h1>
                    </div>
                    <div className="editor-preview-body">
                        <Suspense fallback={<div className="editor-shell-state">レンダリング中...</div>}>
                            <MarkdownRenderer content={note.content || '*プレビューする内容がありません*'} />
                        </Suspense>
                    </div>
                </section>
            </div>

        </div>
    );
}
