"""FastAPI app: serves daily WhatsApp sync results to the frontend and runs
the child_tracker pipeline once a day at 23:00 local via APScheduler.

Run:
    cd backend
    uvicorn api.main:app --reload --port 8000
"""
from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from datetime import date, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Make whatsappmessagesync importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "whatsappmessagesync"))
import child_tracker  # noqa: E402

from . import db  # noqa: E402

scheduler = AsyncIOScheduler()


async def run_daily_sync(target: date | None = None) -> dict:
    """Run sync_day for *target* (default: today) and persist to SQLite."""
    target = target or date.today()
    print(f"[scheduler] Starting sync for {target}")
    try:
        result = await child_tracker.sync_day(target)
    except Exception as exc:
        print(f"[scheduler] Sync FAILED for {target}: {exc}")
        raise
    db.upsert_daily_log(
        date_str=result["date"],
        food_log=result["food_log"],
        behavior_log=result["behavior_log"],
        generated_at=result["generated_at"],
        entries=result["entries"],
    )
    print(f"[scheduler] Sync complete for {target} — persisted to SQLite")
    return result


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    scheduler.add_job(
        run_daily_sync,
        CronTrigger(hour=23, minute=0),  # 23:00 local time daily
        id="daily_whatsapp_sync",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    print("[startup] DB initialised, scheduler started (daily 23:00 local).")
    yield
    scheduler.shutdown()


app = FastAPI(title="SmartHome Organizer API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok", "now": datetime.now().isoformat(timespec="seconds")}


@app.get("/api/daily-logs")
def list_logs():
    """Return [{date, generated_at}, ...] newest first."""
    return db.list_daily_logs()


@app.get("/api/daily-logs/latest")
def latest_log():
    log = db.get_latest_daily_log()
    if not log:
        raise HTTPException(404, "No daily logs yet — run a sync first.")
    return log


@app.get("/api/daily-logs/{date_str}")
def get_log(date_str: str):
    log = db.get_daily_log(date_str)
    if not log:
        raise HTTPException(404, f"No log for {date_str}")
    return log


@app.post("/api/sync")
async def trigger_sync(target_date: str | None = None):
    """Trigger an immediate sync. Optional ?target_date=YYYY-MM-DD."""
    try:
        target = date.fromisoformat(target_date) if target_date else date.today()
    except ValueError:
        raise HTTPException(400, "target_date must be YYYY-MM-DD")
    result = await run_daily_sync(target)
    return {
        "ok": True,
        "date": result["date"],
        "entries_count": len(result["entries"]),
    }
