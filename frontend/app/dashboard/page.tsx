'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import { api, DailyLog, DailyLogSummary } from '@/app/lib/api';

interface User {
  email: string;
  name: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);

  const [logs, setLogs] = useState<DailyLogSummary[]>([]);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [currentLog, setCurrentLog] = useState<DailyLog | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auth gate
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (!userData) {
      router.push('/login');
      return;
    }
    setUser(JSON.parse(userData));
  }, [router]);

  // Initial load: list of available dates + latest log
  const refreshAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const list = await api.listDailyLogs();
      setLogs(list);
      if (list.length > 0) {
        const latest = await api.getDailyLog(list[0].date);
        setCurrentLog(latest);
        setSelectedDate(latest.date);
      } else {
        setCurrentLog(null);
        setSelectedDate(null);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (user) refreshAll();
  }, [user, refreshAll]);

  // Switch selected day
  const selectDate = async (dateStr: string) => {
    if (dateStr === selectedDate) return;
    setLoading(true);
    setError(null);
    try {
      const log = await api.getDailyLog(dateStr);
      setCurrentLog(log);
      setSelectedDate(dateStr);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  const handleSyncNow = async () => {
    setSyncing(true);
    setError(null);
    try {
      await api.triggerSync();
      await refreshAll();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSyncing(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    router.push('/login');
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">👋 Welcome, {user.name}</h1>
            <p className="text-gray-600 text-sm">
              {currentLog
                ? `Viewing log for ${currentLog.date}`
                : 'No logs synced yet'}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleSyncNow}
              disabled={syncing}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            >
              {syncing ? 'Syncing…' : '🔄 Sync Now'}
            </button>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-800 rounded-lg">
            <strong>Error:</strong> {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar: list of dates */}
          <aside className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="text-sm font-bold text-gray-900 mb-3 uppercase tracking-wide">
                Daily Logs
              </h2>
              {logs.length === 0 ? (
                <p className="text-gray-500 text-sm">No logs yet. Click Sync Now.</p>
              ) : (
                <ul className="space-y-1">
                  {logs.map((l) => (
                    <li key={l.date}>
                      <button
                        onClick={() => selectDate(l.date)}
                        className={`w-full text-left px-3 py-2 rounded text-sm transition ${
                          selectedDate === l.date
                            ? 'bg-blue-100 text-blue-900 font-semibold'
                            : 'text-gray-700 hover:bg-gray-100'
                        }`}
                      >
                        {l.date}
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </aside>

          {/* Main: food + behavior markdown */}
          <section className="lg:col-span-3 space-y-6">
            {loading && <p className="text-gray-500">Loading…</p>}

            {!loading && !currentLog && (
              <div className="bg-white rounded-lg shadow p-8 text-center">
                <p className="text-gray-600 mb-4">
                  No daily logs available yet.
                </p>
                <p className="text-gray-500 text-sm">
                  Make sure the WhatsApp bridge, Parakeet, and local LLM are
                  running, then click <strong>Sync Now</strong>.
                </p>
              </div>
            )}

            {!loading && currentLog && (
              <>
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">
                    🍽️ Food Log
                  </h2>
                  <div className="prose prose-sm max-w-none text-gray-800">
                    <ReactMarkdown>{currentLog.food_log}</ReactMarkdown>
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">
                    😊 Behavior &amp; Mood Log
                  </h2>
                  <div className="prose prose-sm max-w-none text-gray-800">
                    <ReactMarkdown>{currentLog.behavior_log}</ReactMarkdown>
                  </div>
                </div>

                <details className="bg-white rounded-lg shadow p-6">
                  <summary className="cursor-pointer font-semibold text-gray-900">
                    📝 Raw entries ({currentLog.entries.length})
                  </summary>
                  <ul className="mt-3 space-y-1 text-sm text-gray-700">
                    {currentLog.entries.map((e, i) => (
                      <li key={i} className="font-mono">{e}</li>
                    ))}
                  </ul>
                </details>

                <p className="text-xs text-gray-500 text-right">
                  Generated {currentLog.generated_at}
                </p>
              </>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}
