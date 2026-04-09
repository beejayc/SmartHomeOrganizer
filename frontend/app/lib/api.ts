// Backend API client. Backend runs on http://localhost:8000 (FastAPI).
const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000';

export interface DailyLogSummary {
  date: string;          // YYYY-MM-DD
  generated_at: string;
}

export interface DailyLog extends DailyLogSummary {
  food_log: string;      // markdown
  behavior_log: string;  // markdown
  entries: string[];
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

export const api = {
  listDailyLogs: () => get<DailyLogSummary[]>('/api/daily-logs'),
  getDailyLog: (date: string) => get<DailyLog>(`/api/daily-logs/${date}`),
  getLatest: () => get<DailyLog>('/api/daily-logs/latest'),
  triggerSync: async (date?: string): Promise<{ ok: boolean; date: string; entries_count: number }> => {
    const qs = date ? `?target_date=${date}` : '';
    const res = await fetch(`${API_BASE}/api/sync${qs}`, { method: 'POST' });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json();
  },
};
