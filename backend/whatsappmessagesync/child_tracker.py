#!/usr/bin/env python3
"""
Child Daily Log Tracker
-----------------------
Reads today's messages and voice notes from the "Ilan Tracker" WhatsApp group
via the whatsapp-mcp MCP server, transcribes audio using a local Parakeet
speech-to-text server (OpenAI-compatible API), and uses a local LLM (also
OpenAI-compatible) to split entries into dated food and behavior/mood log files.

Usage:
    python child_tracker.py                    # process today
"""

import os
import sys
import re
import json
import asyncio
import argparse
import tempfile
from datetime import datetime, date, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
WHATSAPP_CHAT_NAME = "Ilan Tracker"

# Local Parakeet STT server (OpenAI-compatible)
PARAKEET_URL = os.environ.get("PARAKEET_URL", "http://localhost:5092")
PARAKEET_MODEL = os.environ.get("PARAKEET_MODEL", "parakeet-tdt-0.6b-v3")

# Local LLM server (OpenAI-compatible)
LLM_URL =  "http://localhost:30000"
LOCAL_LLM_URL = LLM_URL
# os.environ.get("LOCAL_LLM_URL", "http://127.0.0.1:8080")
LOCAL_LLM_MODEL = os.environ.get("LOCAL_LLM_MODEL", "Qwen3.5-35B-A3B")

stt_client = OpenAI(base_url=PARAKEET_URL + "/v1", api_key="not-needed")
llm_client = OpenAI(base_url=LOCAL_LLM_URL + "/v1", api_key="dummy-key")

LOG_DIR = Path("logs")
FOOD_DIR = LOG_DIR / "food"
BEHAVIOR_DIR = LOG_DIR / "behavior"

# Audio MIME types recognized as voice notes / audio messages
AUDIO_MIMETYPES = {
    "audio/mpeg", "audio/mp4", "audio/ogg", "audio/webm",
    "audio/wav", "audio/x-m4a", "audio/aac", "audio/flac", "audio/opus",
}

# WhatsApp message types that carry audio
AUDIO_MSG_TYPES = {"audio", "ptt"}  # ptt = push-to-talk (voice note)

# ---------------------------------------------------------------------------
# WhatsApp MCP helpers
# ---------------------------------------------------------------------------

async def find_chat_jid(session, chat_name: str) -> str | None:
    """Find the JID of the first chat whose name contains *chat_name*.

    FastMCP returns each list item as a separate TextContent block, each
    containing a single JSON object with 'jid' and 'name' keys.
    """
    result = await session.call_tool("list_chats", {"query": chat_name, "limit": 20})
    if not result.content:
        return None
    for block in result.content:
        text = getattr(block, "text", "") or ""
        try:
            chat = json.loads(text)
            if isinstance(chat, dict) and chat_name.lower() in (chat.get("name") or "").lower():
                return chat.get("jid")
        except json.JSONDecodeError:
            continue
    return None


async def fetch_whatsapp_messages(session, chat_jid: str, target_date: date) -> str:
    """Return formatted message text for *chat_jid* on *target_date* (UTC)."""
    day_start = datetime(target_date.year, target_date.month, target_date.day,
                         0, 0, 0, tzinfo=timezone.utc)
    day_end = datetime(target_date.year, target_date.month, target_date.day,
                       23, 59, 59, tzinfo=timezone.utc)

    result = await session.call_tool("list_messages", {
        "chat_jid": chat_jid,
        "after": day_start.isoformat(),
        "before": day_end.isoformat(),
        "limit": 500,
        "include_context": False,
    })

    if not result.content:
        return ""
    return getattr(result.content[0], "text", "") or ""


async def download_whatsapp_media(session, message_id: str, chat_jid: str) -> bytes | None:
    """Download a media file and return its raw bytes (or None on failure)."""
    try:
        result = await session.call_tool("download_media", {
            "message_id": message_id,
            "chat_jid": chat_jid,
        })
        if not result.content:
            return None
        text = getattr(result.content[0], "text", "") or ""
        # Response is {"success": true, "file_path": "..."}
        try:
            data = json.loads(text)
            if data.get("success") and data.get("file_path"):
                path = data["file_path"]
                if os.path.isfile(path):
                    return Path(path).read_bytes()
        except (json.JSONDecodeError, KeyError):
            pass
        # Fallback: treat text as a bare file path
        path = text.strip()
        if os.path.isfile(path):
            return Path(path).read_bytes()
    except Exception as exc:
        print(f"    Warning: could not download media — {exc}")
    return None


# ---------------------------------------------------------------------------
# Audio transcription
# ---------------------------------------------------------------------------

def transcribe_audio_bytes(audio_bytes: bytes, ext: str) -> str:
    """Write *audio_bytes* to a temp file and transcribe it via the local
    Parakeet STT server using the OpenAI-compatible audio.transcriptions API."""
    suffix = ext if ext.startswith(".") else f".{ext}"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            transcript = stt_client.audio.transcriptions.create(
                model=PARAKEET_MODEL,
                file=f,
                response_format="text",
            )
        # response_format="text" returns a plain string
        return (transcript if isinstance(transcript, str) else getattr(transcript, "text", "")).strip()
    except Exception as exc:
        print(f"    Warning: transcription failed — {exc}")
        return ""
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Entry collection
# ---------------------------------------------------------------------------

_EXT_BY_MIMETYPE = {
    "audio/ogg": "ogg",
    "audio/mpeg": "mp3",
    "audio/mp4": "m4a",
    "audio/webm": "webm",
    "audio/aac": "aac",
    "audio/opus": "opus",
    "audio/wav": "wav",
}


def _is_audio_message(msg: dict) -> bool:
    mimetype = msg.get("mimetype", "") or msg.get("media_type", "")
    msg_type = msg.get("type", "").lower()
    return mimetype in AUDIO_MIMETYPES or msg_type in AUDIO_MSG_TYPES


def _parse_timestamp(msg: dict) -> float:
    ts_raw = msg.get("timestamp", 0)
    if isinstance(ts_raw, str):
        try:
            return datetime.fromisoformat(ts_raw).timestamp()
        except ValueError:
            return 0.0
    return float(ts_raw)


async def collect_entries(session, messages_text: str, chat_jid: str) -> list[str]:
    """
    Parse the formatted message string from list_messages, transcribe any voice
    notes encountered, and return a flat list of timestamped text entries.

    Each line from the MCP server looks like:
      [YYYY-MM-DD HH:MM:SS] Chat: Name From: Sender: <content>
    Audio lines have content like:
      [audio - Message ID: <id> - Chat JID: <jid>] <optional-caption>
    """
    entries: list[str] = []
    # Pattern: [YYYY-MM-DD HH:MM:SS] ...
    line_re = re.compile(r'^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s*(.*)', re.DOTALL)
    # Audio/ptt marker embedded in content
    audio_re = re.compile(r'\[(audio|ptt)[^\]]*Message ID:\s*([^\s\]-]+)[^\]]*\]', re.IGNORECASE)

    for line in messages_text.splitlines():
        line = line.strip()
        if not line:
            continue

        m = line_re.match(line)
        if not m:
            continue

        try:
            msg_time = datetime.fromisoformat(m.group(1)).strftime("%I:%M %p")
        except ValueError:
            msg_time = "??:??"

        rest = m.group(2)
        # Strip "Chat: <name> From: <sender>: " prefix
        content_match = re.search(r'From: [^:]+:\s*(.*)', rest, re.DOTALL)
        content = content_match.group(1).strip() if content_match else rest.strip()

        audio_m = audio_re.search(content)
        if audio_m:
            msg_id = audio_m.group(2)
            print(f"    Transcribing voice note {msg_id[:8]}…")
            audio_bytes = await download_whatsapp_media(session, msg_id, chat_jid)
            if audio_bytes:
                transcription = transcribe_audio_bytes(audio_bytes, "ogg")
                if transcription:
                    entries.append(f"[{msg_time}] (Voice note) {transcription}")
                else:
                    entries.append(f"[{msg_time}] (Voice note — transcription unavailable)")
            else:
                entries.append(f"[{msg_time}] (Voice note — download failed)")
        elif content:
            entries.append(f"[{msg_time}] {content}")

    return entries


# ---------------------------------------------------------------------------
# Claude parsing
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a child health and wellbeing tracker assistant.
A parent logs their child's day via voice notes and text messages in WhatsApp.
Your job is to read the raw, unstructured log entries and produce two clean,
readable reports:

1. FOOD LOG  — everything about food, drinks, appetite, meals, snacks,
   feeding times, food refusals, or nutrition observations.

2. BEHAVIOR & MOOD LOG — everything about emotions, behavior, temperament,
   tantrums, happiness, energy levels, sleep, naps, activities, milestones,
   and social interactions.

Rules:
- Keep every piece of information; do not summarise away details.
- Preserve times where they appear.
- Format as bullet points grouped by time of day (Morning / Afternoon / Evening)
  when there is enough information, otherwise just use bullet points.
- If a category has no information at all, write exactly: "No entries recorded."
- Return ONLY a JSON object — no markdown fences, no extra keys — with exactly
  two string keys: "food_log" and "behavior_log".
"""


def parse_with_llm(entries: list[str], target_date: date) -> tuple[str, str]:
    """Send entries to the local LLM (OpenAI-compatible chat completions) and
    return (food_log, behavior_log) markdown strings."""
    date_str = target_date.strftime("%A, %B %d, %Y")
    entries_text = "\n".join(entries) if entries else "No entries were recorded today."

    user_prompt = f"""Date: {date_str}

Raw log entries from WhatsApp:
---
{entries_text}
---

Split the above entries into a food log and a behavior & mood log.
Return JSON with keys "food_log" and "behavior_log".
Each value should be a self-contained markdown string ready to save as a file."""

    try:
        completion = llm_client.chat.completions.create(
            model=LOCAL_LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        text_content = (completion.choices[0].message.content or "").strip()
    except Exception as exc:
        print(f"    Warning: local LLM error — {exc}")
        text_content = ""

    # Strip any accidental markdown fences the model might add
    text_content = re.sub(r"```(?:json)?", "", text_content).strip().rstrip("`")

    try:
        data = json.loads(text_content)
        return data.get("food_log", "No entries recorded."), data.get("behavior_log", "No entries recorded.")
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', text_content, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                return data.get("food_log", "No entries recorded."), data.get("behavior_log", "No entries recorded.")
            except json.JSONDecodeError:
                pass
        fallback = "Parsing error — raw entries below:\n\n" + entries_text
        return fallback, fallback


# ---------------------------------------------------------------------------
# File writing
# ---------------------------------------------------------------------------

def write_log(content: str, filepath: Path, target_date: date, log_type: str) -> None:
    """Write a markdown log file with a title header and generation timestamp."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    header = f"# Child {log_type} — {target_date.strftime('%A, %B %d, %Y')}\n\n"
    footer = (
        f"\n\n---\n"
        f"*Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} "
        f"by child_tracker.py*\n"
    )

    filepath.write_text(header + content + footer, encoding="utf-8")
    print(f"  Saved: {filepath}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def sync_day(target_date: date) -> dict:
    """Run the full pipeline for *target_date* and return a dict:
        {date, food_log, behavior_log, entries, generated_at}

    Does NOT write any files. Used by both the CLI wrapper and the FastAPI
    backend.
    """
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    date_str = target_date.strftime("%Y-%m-%d")
    chat_name = WHATSAPP_CHAT_NAME

    print(f"\n{'─' * 52}")
    print(f"  Child Log Tracker  |  {date_str}")
    print(f"{'─' * 52}\n")
    print(f"[1/4] Parakeet STT @ {PARAKEET_URL} ({PARAKEET_MODEL})")
    print(f"      Local LLM    @ {LOCAL_LLM_URL} ({LOCAL_LLM_MODEL})\n")

    server_params = StdioServerParameters(
        command="uv",
        args=["run", "main.py"],
        cwd="/home/chandbla/AnthropicExpers/whatsapp-mcp/whatsapp-mcp-server",
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print(f"[2/4] Fetching messages for {date_str} …")
            chat_jid = await find_chat_jid(session, chat_name)
            if not chat_jid:
                raise RuntimeError(f"No WhatsApp chat found matching '{chat_name}'")

            messages_text = await fetch_whatsapp_messages(session, chat_jid, target_date)
            line_count = sum(1 for l in messages_text.splitlines() if l.strip())
            print(f"      {line_count} message line(s) found in '{chat_name}'.\n")

            print("[3/4] Transcribing voice notes …")
            entries = await collect_entries(session, messages_text, chat_jid)
            print(f"      {len(entries)} entries collected.\n")

    print(f"[4/4] Analysing with local LLM '{LOCAL_LLM_MODEL}' …")
    food_log, behavior_log = parse_with_llm(entries, target_date)
    print("      Done.\n")

    return {
        "date": date_str,
        "food_log": food_log,
        "behavior_log": behavior_log,
        "entries": entries,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


async def run(args) -> None:
    """CLI entry point — runs sync_day and also writes markdown files."""
    target_date = date.today()
    result = await sync_day(target_date)
    date_str = result["date"]

    print("Writing log files …")
    food_path = FOOD_DIR / f"{date_str}_food.md"
    behavior_path = BEHAVIOR_DIR / f"{date_str}_behavior.md"
    write_log(result["food_log"], food_path, target_date, "Food Log")
    write_log(result["behavior_log"], behavior_path, target_date, "Behavior & Mood Log")

    print(f"\n✓ Logs saved for {date_str}")
    print(f"  {food_path}")
    print(f"  {behavior_path}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Process today\'s "Ilan Tracker" WhatsApp logs into food and behavior files.'
    )
    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
