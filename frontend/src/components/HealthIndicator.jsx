import { useState, useEffect, useCallback, useRef } from 'react';
import { fetchHealth, fetchHealthDetailed } from '../api/health';
import './HealthIndicator.css';

const POLL_INTERVAL_MS = 30_000;   // 30秒
const FAILURE_THRESHOLD = 3;        // 3回連続失敗で異常判定

/**
 * HealthIndicator — 全ページ共通フッターのシステムステータスインジケーター。
 *
 * - 30秒ごとに GET /api/v1/health/ をポーリング
 * - 3回連続失敗したら異常（🔴）と判定
 * - 成功したら即座に 🟢 に復帰
 * - クリックで詳細モーダル展開（DB状態、稼働時間、ノート数 等）
 */
export default function HealthIndicator() {
  const [status, setStatus] = useState('loading');   // 'ok' | 'error' | 'loading'
  const [failureCount, setFailureCount] = useState(0);
  const [modalOpen, setModalOpen] = useState(false);
  const [details, setDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const ignoreRef = useRef(false);

  // ── ヘルスチェックポーリング ──
  const check = useCallback(async () => {
    try {
      const data = await fetchHealth();
      if (ignoreRef.current) return;
      // HTTP 200 でも db が false または status が degraded → error
      if (data.db === false || data.status === 'degraded') {
        setStatus('error');
      } else {
        setStatus('ok');
      }
      setFailureCount(0);
    } catch {
      if (ignoreRef.current) return;
      setFailureCount(prev => {
        const next = prev + 1;
        if (next >= FAILURE_THRESHOLD) {
          setStatus('error');
        }
        return next;
      });
    }
  }, []);

  useEffect(() => {
    ignoreRef.current = false;
    check();                               // 初回即実行
    const timer = setInterval(check, POLL_INTERVAL_MS);
    return () => {
      ignoreRef.current = true;
      clearInterval(timer);
    };
  }, [check]);

  // ── モーダル開閉 ──
  const openModal = useCallback(async () => {
    setModalOpen(true);
    setDetailsLoading(true);
    try {
      const data = await fetchHealthDetailed();
      if (!ignoreRef.current) {
        setDetails(data);
      }
    } catch {
      if (!ignoreRef.current) {
        setDetails({ status: 'error', details: {} });
      }
    } finally {
      if (!ignoreRef.current) {
        setDetailsLoading(false);
      }
    }
  }, []);

  const closeModal = useCallback(() => {
    setModalOpen(false);
    setDetails(null);
  }, []);

  // ── ドットの色とテキスト ──
  let dotClass, labelText;
  if (status === 'loading') {
    dotClass = 'dot-loading';
    labelText = '確認中';
  } else if (status === 'ok') {
    dotClass = 'dot-ok';
    labelText = '正常';
  } else {
    dotClass = 'dot-error';
    labelText = '異常';
  }

  // ── 詳細情報の整形 ──
  const detailItems = [];
  if (details?.details) {
    const d = details.details;
    if (d.db !== undefined) {
      detailItems.push({ label: 'データベース', value: typeof d.db === 'string' && d.db !== 'ok' ? d.db : '接続OK' });
    }
    if (d.uptime_seconds !== undefined) {
      const s = d.uptime_seconds;
      const h = Math.floor(s / 3600);
      const m = Math.floor((s % 3600) / 60);
      detailItems.push({ label: '稼働時間', value: `${h}h ${m}m` });
    }
    if (d.notes !== undefined) {
      detailItems.push({ label: 'ノート数', value: d.notes });
    }
    if (d.categories !== undefined) {
      detailItems.push({ label: 'カテゴリ数', value: d.categories });
    }
  }

  return (
    <>
      {/* ── ステータスドット ── */}
      <button
        type="button"
        className={`health-indicator ${dotClass}`}
        onClick={openModal}
        title={labelText}
        aria-label={`システムステータス: ${labelText}`}
      >
        <span className="health-dot" aria-hidden="true" />
        <span className="health-label">{labelText}</span>
      </button>

      {/* ── 詳細モーダル ── */}
      {modalOpen && (
        <div className="health-modal-overlay" onClick={closeModal}>
          <div className="health-modal" onClick={e => e.stopPropagation()} role="dialog" aria-label="システム詳細情報">
            <div className="health-modal-header">
              <h2>システムステータス</h2>
              <button type="button" className="health-modal-close" onClick={closeModal} aria-label="閉じる">
                ✕
              </button>
            </div>

            <div className="health-modal-body">
              {detailsLoading ? (
                <p className="health-modal-loading">読み込み中...</p>
              ) : details?.status === 'error' ? (
                <p className="health-modal-error">詳細情報の取得に失敗しました</p>
              ) : detailItems.length > 0 ? (
                <dl className="health-detail-list">
                  {detailItems.map(item => (
                    <div key={item.label} className="health-detail-row">
                      <dt>{item.label}</dt>
                      <dd>{item.value}</dd>
                    </div>
                  ))}
                </dl>
              ) : (
                <p className="health-modal-empty">詳細情報がありません</p>
              )}
            </div>

            <div className="health-modal-footer">
              <span className={`health-modal-status ${dotClass}`}>
                <span className="health-dot" aria-hidden="true" />
                {labelText}
              </span>
              <button type="button" className="health-modal-close-btn" onClick={closeModal}>
                閉じる
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
