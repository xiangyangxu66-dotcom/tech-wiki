import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import HealthIndicator from '../src/components/HealthIndicator';

// ── Mock health API ──
const mockFetchHealth = vi.fn();
const mockFetchHealthDetailed = vi.fn();

vi.mock('../src/api/health', () => ({
  fetchHealth: () => mockFetchHealth(),
  fetchHealthDetailed: () => mockFetchHealthDetailed(),
}));

// ── Helper: flush fake-timer promises ──
async function flushMicrotasks() {
  await act(() => vi.advanceTimersByTime(0));
}

function advancePollCycle() {
  act(() => { vi.advanceTimersByTime(30_000); });
}

describe('HealthIndicator', () => {
  beforeEach(() => {
    mockFetchHealth.mockReset();
    mockFetchHealthDetailed.mockReset();
  });

  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // Group A: Single-render tests (no polling needed → real timers)
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  describe('single render (real timers)', () => {
    it('shows loading state initially', () => {
      mockFetchHealth.mockReturnValue(new Promise(() => {}));
      render(<HealthIndicator />);
      expect(screen.getByText('確認中')).toBeInTheDocument();
    });

    it('shows ok dot when health check succeeds', async () => {
      mockFetchHealth.mockResolvedValue({ status: 'ok', db: true });
      render(<HealthIndicator />);
      await waitFor(() => {
        expect(screen.getByText('正常')).toBeInTheDocument();
      });
    });

    it('shows error when db is false', async () => {
      mockFetchHealth.mockResolvedValue({ status: 'degraded', db: false });
      render(<HealthIndicator />);
      await waitFor(() => {
        expect(screen.getByText('異常')).toBeInTheDocument();
      });
    });

    it('shows error when status is "degraded"', async () => {
      mockFetchHealth.mockResolvedValue({ status: 'degraded', db: true });
      render(<HealthIndicator />);
      await waitFor(() => {
        expect(screen.getByText('異常')).toBeInTheDocument();
      });
    });

    it('opens modal on dot click', async () => {
      mockFetchHealth.mockResolvedValue({ status: 'ok', db: true });
      render(<HealthIndicator />);
      await waitFor(() => {
        expect(screen.getByText('正常')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByRole('button', { name: /システムステータス/ }));
      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });
    });

    it('closes modal on ✕ button click', async () => {
      mockFetchHealth.mockResolvedValue({ status: 'ok', db: true });
      render(<HealthIndicator />);
      await waitFor(() => {
        expect(screen.getByText('正常')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByRole('button', { name: /システムステータス/ }));
      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });

      // Close via footer's close button (use the one with text "閉じる")
      const closeButtons = screen.getAllByRole('button', { name: '閉じる' });
      fireEvent.click(closeButtons[0]);
      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });
    });

    it('closes modal on overlay click', async () => {
      mockFetchHealth.mockResolvedValue({ status: 'ok', db: true });
      render(<HealthIndicator />);
      await waitFor(() => {
        expect(screen.getByText('正常')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByRole('button', { name: /システムステータス/ }));
      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });

      // Click the overlay
      const overlay = document.querySelector('.health-modal-overlay');
      fireEvent.click(overlay);
      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });
    });

    it('shows detailed info in modal', async () => {
      mockFetchHealth.mockResolvedValue({ status: 'ok', db: true });
      mockFetchHealthDetailed.mockResolvedValue({
        status: 'ok',
        details: { db: 'ok', uptime_seconds: 3661, notes: 42, categories: 7 },
      });

      render(<HealthIndicator />);
      await waitFor(() => {
        expect(screen.getByText('正常')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByRole('button', { name: /システムステータス/ }));

      await waitFor(() => {
        expect(screen.getByText('データベース')).toBeInTheDocument();
        expect(screen.getByText('接続OK')).toBeInTheDocument();
        expect(screen.getByText('1h 1m')).toBeInTheDocument();
        expect(screen.getByText('42')).toBeInTheDocument();
        expect(screen.getByText('7')).toBeInTheDocument();
      });
    });

    it('shows db error text when db is not ok', async () => {
      mockFetchHealth.mockResolvedValue({ status: 'ok', db: true });
      mockFetchHealthDetailed.mockResolvedValue({
        status: 'degraded',
        details: { db: 'connection refused', uptime_seconds: 0, notes: 0 },
      });

      render(<HealthIndicator />);
      await waitFor(() => {
        expect(screen.getByText('正常')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByRole('button', { name: /システムステータス/ }));

      await waitFor(() => {
        expect(screen.getByText('connection refused')).toBeInTheDocument();
      });
    });

    it('shows error message when detailed API fails', async () => {
      mockFetchHealth.mockResolvedValue({ status: 'ok', db: true });
      mockFetchHealthDetailed.mockRejectedValue(new Error('fail'));

      render(<HealthIndicator />);
      await waitFor(() => {
        expect(screen.getByText('正常')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByRole('button', { name: /システムステータス/ }));

      await waitFor(() => {
        expect(screen.getByText('詳細情報の取得に失敗しました')).toBeInTheDocument();
      });
    });
  });

  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  // Group B: Polling-accumulation tests (need fake timers)
  // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  describe('polling (fake timers)', () => {
    beforeEach(() => { vi.useFakeTimers(); });
    afterEach(() => { vi.useRealTimers(); });

    it('shows error after 3 consecutive failures', async () => {
      mockFetchHealth.mockRejectedValue(new Error('Network error'));

      render(<HealthIndicator />);

      // Flush initial check
      await flushMicrotasks();
      // 2nd failure
      advancePollCycle();
      await flushMicrotasks();
      // 3rd failure → error
      advancePollCycle();
      await flushMicrotasks();

      expect(screen.getByText('異常')).toBeInTheDocument();
    });

    it('remains loading after only 2 failures (not error)', async () => {
      mockFetchHealth.mockRejectedValue(new Error('Network error'));

      render(<HealthIndicator />);

      await flushMicrotasks();
      advancePollCycle();
      await flushMicrotasks();

      // 2 failures only — not yet error
      expect(screen.queryByText('異常')).not.toBeInTheDocument();
    });

    it('recovers to ok after failure streak is broken', async () => {
      // Fail 3 times
      mockFetchHealth.mockRejectedValue(new Error('fail'));

      render(<HealthIndicator />);

      await flushMicrotasks();
      advancePollCycle();
      await flushMicrotasks();
      advancePollCycle();
      await flushMicrotasks();

      expect(screen.getByText('異常')).toBeInTheDocument();

      // Now succeed
      mockFetchHealth.mockResolvedValue({ status: 'ok', db: true });
      advancePollCycle();
      await flushMicrotasks();

      expect(screen.getByText('正常')).toBeInTheDocument();
    });
  });
});
