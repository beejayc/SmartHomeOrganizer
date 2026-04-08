# CLAUDE.md — Backend

Guidance for Claude Code when working in `backend/`. The root `CLAUDE.md` covers project-wide context; this file is backend-specific.

---

## Current Sprint: FastAPI + SQLite + Daily Sync

Sprint goal (delivered): wrap the existing `child_tracker.py` pipeline in a
FastAPI service that runs the sync once a day at **23:00 local** via
APScheduler, persists results to a local SQLite database, and exposes them via
HTTP for the frontend dashboard. The frontend now reads exclusively from this
backend (no more `mockData.ts`).

Previous sprint built the WhatsApp → Parakeet STT → local LLM pipeline; that
code still lives in `whatsappmessagesync/` and is now invoked from the API
layer instead of being a CLI-only script.

---

## Architecture

```
WhatsApp ──► whatsapp-bridge (Go)  ──► whatsapp-mcp-server (Python, stdio MCP)
                                              │
                                              ▼
                                child_tracker.sync_day(date)
                                       │        │
                       ┌───────────────┘        └────────────────┐
                       ▼                                         ▼
            Parakeet STT (OpenAI API)                Local LLM (OpenAI API)
            http://localhost:5092                    http://localhost:30000
            model: parakeet-tdt-0.6b-v3              model: Qwen3.5-35B-A3B
                       │                                         │
                       └───────────────┬─────────────────────────┘
                                       ▼
                              FastAPI (api/main.py)
                                       │
                       ┌───────────────┼────────────────┐
                       ▼               ▼                ▼
                  SQLite           HTTP /api/*     APScheduler
                  data/            (CORS for       cron 23:00
                  smarthome.db     :3000)          local daily
                                       │
                                       ▼
                            frontend dashboard (Next.js)
```

Both STT and LLM are accessed via the **OpenAI Python SDK** pointed at local
base URLs — no real OpenAI calls, no API keys.

---

## Layout

```
backend/
├── api/
│   ├── __init__.py
│   ├── db.py          # SQLite schema + upsert/get/list helpers
│   └── main.py        # FastAPI app, lifespan starts APScheduler
├── data/
│   └── smarthome.db   # auto-created on first startup
├── whatsappmessagesync/
│   ├── child_tracker.py   # sync_day() callable + CLI run()
│   ├── requirements.txt   # all backend deps (api + tracker)
│   ├── venv/              # python venv (use this for both api and CLI)
│   └── logs/              # markdown files written by CLI run() only
└── CLAUDE.md         # this file
```

`venv/` lives under `whatsappmessagesync/` for historical reasons; it's the
single venv used by both the API and the CLI. Run the API with
`./whatsappmessagesync/venv/bin/uvicorn ...` from the `backend/` directory.

---

## Key files

- **`api/main.py`** — FastAPI app.
  - `lifespan()` initialises the DB and starts APScheduler with a single cron
    job (`hour=23, minute=0`) that calls `run_daily_sync()`.
  - `run_daily_sync(target)` — invokes `child_tracker.sync_day(target)` then
    `db.upsert_daily_log(...)`. Used by both the cron job and the manual
    `POST /api/sync` endpoint.
  - CORS is locked to `http://localhost:3000`.
- **`api/db.py`** — sqlite3 (stdlib, no ORM).
  - `daily_logs(date PK, food_log, behavior_log, generated_at)` — one row per day.
  - `raw_entries(id, date FK, idx, content)` — per-day ordered raw entries
    (text + transcribed voice notes), used for traceability and the
    "Raw entries" disclosure in the dashboard.
  - `upsert_daily_log` replaces both the daily row and its raw_entries
    atomically — safe to re-run a sync for the same day.
- **`whatsappmessagesync/child_tracker.py`** — pipeline.
  - `async sync_day(date) -> dict` is the **callable entry point** for the
    API. Returns `{date, food_log, behavior_log, entries, generated_at}`.
    Does **not** write any files.
  - `async run(args)` is the CLI wrapper: calls `sync_day` and additionally
    writes markdown files under `logs/food/` and `logs/behavior/`. Kept for
    backward compat — the API doesn't use it.

---

## HTTP API

| Method | Path | Purpose |
|---|---|---|
| GET  | `/api/health` | Liveness check |
| GET  | `/api/daily-logs` | List `[{date, generated_at}]` newest first |
| GET  | `/api/daily-logs/latest` | Most recent full log |
| GET  | `/api/daily-logs/{YYYY-MM-DD}` | One day's full log (food + behavior + entries) |
| POST | `/api/sync?target_date=YYYY-MM-DD` | Run pipeline immediately (defaults to today) |

The frontend client lives at `frontend/app/lib/api.ts`.

---

## Running

Three external services must be up:

```bash
# 1. WhatsApp bridge (Go)
cd whatsapp-mcp-go/whatsapp-bridge && go run main.go

# 2. Parakeet STT server   → http://localhost:5092 (docker)
# 3. Local LLM server      → http://localhost:30000 (Qwen3.5-35B-A3B)
```

Then start the API (which also runs the 23:00 scheduler):

```bash
cd backend
./whatsappmessagesync/venv/bin/uvicorn api.main:app --reload --port 8000
```

Trigger a sync immediately:

```bash
curl -X POST http://localhost:8000/api/sync
# or, from the dashboard, click "Sync Now"
```

CLI-only run (also writes markdown files; bypasses DB):

```bash
cd backend/whatsappmessagesync
./venv/bin/python child_tracker.py
```

---

## Configuration (env vars)

| Var | Default | Purpose |
|---|---|---|
| `PARAKEET_URL`     | `http://localhost:5092`  | Parakeet STT base URL |
| `PARAKEET_MODEL`   | `parakeet-tdt-0.6b-v3`   | STT model name |
| `LOCAL_LLM_URL`    | `http://localhost:30000` (currently hard-coded in `child_tracker.py`) | Local LLM base URL |
| `LOCAL_LLM_MODEL`  | `Qwen3.5-35B-A3B`        | LLM model name |

`.env` is loaded via `python-dotenv` at module import. Note: `LOCAL_LLM_URL`
is currently hard-coded in `child_tracker.py` to `http://localhost:30000`;
the env var is ignored. Fix this before relying on env-based config.

---

## Conventions & gotchas

- **Single source of truth = SQLite.** The API never reads the markdown files
  under `logs/`. Those are CLI-mode only.
- **APScheduler is in-process**, started in the FastAPI lifespan. The
  scheduler stops when uvicorn stops — there is no separate worker process
  and no persistence across restarts. A missed 23:00 run is *not*
  automatically retried beyond `misfire_grace_time=3600` (1 hour).
- **`upsert_daily_log` deletes-and-reinserts `raw_entries`** for the day —
  never accumulate duplicates by appending.
- **OpenAI SDK only** for both STT and LLM — do not reintroduce the `whisper`
  package or the `claude` CLI subprocess.
- **WhatsApp chat name** is hard-coded as `Ilan Tracker`
  (`WHATSAPP_CHAT_NAME`). `find_chat_jid` does a case-insensitive substring
  match.
- **MCP server path** is hard-coded inside `child_tracker.sync_day` to
  `/home/chandbla/AnthropicExpers/whatsapp-mcp/whatsapp-mcp-server`. Update
  if the repo layout changes.
- **MCP `list_messages` line format** — `[YYYY-MM-DD HH:MM:SS] Chat: X From: Y: <content>`,
  with audio marked as `[audio - Message ID: <id> - Chat JID: <jid>]`. The
  regexes in `collect_entries` depend on this exact shape.
- **LLM JSON parsing** — `parse_with_llm` strips stray markdown fences and
  falls back to a regex-extracted `{...}` if the model wraps the JSON.
- **Known data quirk** — observed duplicate raw entries when the same voice
  note Message ID appears twice in a fetch. Worth investigating in
  `collect_entries` next iteration.

---

## Not yet built

- Auth (frontend still uses fake localStorage session).
- PostgreSQL migration (root CLAUDE.md's long-term plan; SQLite is the
  deliberate MVP choice).
- Activity logging endpoints (POST). The current API is read-only plus the
  one `/api/sync` trigger.
- Tests.
- Background task queue (Redis). APScheduler in-process is the MVP.
