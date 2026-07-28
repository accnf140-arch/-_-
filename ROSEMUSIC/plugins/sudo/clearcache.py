# -----------------------------------------------
# 🔸 Rose X Music — /clearcache command
# Clears downloads, thumbnail cache, and old RAM
# Auto-runs every 30 minutes via scheduler
# -----------------------------------------------
import asyncio
import gc
import glob
import os
import time

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import filters
from pyrogram.types import Message

import config
from SHUKLAMUSIC import app
from SHUKLAMUSIC.misc import SUDOERS

# ── Directories to clean ──────────────────────────────────────────────────────
_DOWNLOAD_DIR = "downloads"
_CACHE_DIR = "cache"
# Keep files newer than this (seconds) — protects files in active use
_KEEP_IF_NEWER_THAN = 300   # 5 minutes


def _clean_dir(path: str, keep_recent: bool = True) -> tuple[int, float]:
    """Delete files in *path*. Returns (count_deleted, mb_freed)."""
    removed = 0
    freed = 0.0
    if not os.path.isdir(path):
        return removed, freed
    now = time.time()
    for f in glob.glob(os.path.join(path, "*")):
        if not os.path.isfile(f):
            continue
        if keep_recent and (now - os.path.getmtime(f)) < _KEEP_IF_NEWER_THAN:
            continue
        try:
            size = os.path.getsize(f)
            os.remove(f)
            removed += 1
            freed += size
        except Exception:
            pass
    return removed, freed / (1024 * 1024)


async def do_clearcache(force: bool = False) -> str:
    """Run the full cache-clean and return a human-readable report."""
    loop = asyncio.get_event_loop()

    dl_count, dl_mb = await loop.run_in_executor(
        None, _clean_dir, _DOWNLOAD_DIR, not force
    )
    ca_count, ca_mb = await loop.run_in_executor(
        None, _clean_dir, _CACHE_DIR, not force
    )

    # Force Python GC to release RAM
    collected = gc.collect()

    total_mb = round(dl_mb + ca_mb, 2)
    report = (
        f"🧹 **Cache Cleared!**\n\n"
        f"📂 Downloads: `{dl_count}` files removed (`{round(dl_mb, 2)} MB`)\n"
        f"🖼 Thumbnails: `{ca_count}` files removed (`{round(ca_mb, 2)} MB`)\n"
        f"💾 Total freed: `{total_mb} MB`\n"
        f"🔄 GC objects collected: `{collected}`"
    )
    return report


# ── /clearcache command ───────────────────────────────────────────────────────
@app.on_message(filters.command(["clearcache", "cacheclean", "clearall"]) & SUDOERS)
async def clearcache_cmd(client, message: Message):
    msg = await message.reply_text("🧹 Clearing cache, please wait...")
    report = await do_clearcache(force=True)
    await msg.edit_text(report)


# ── Auto-clean scheduler (every 30 minutes) ──────────────────────────────────
_scheduler = AsyncIOScheduler()


async def _auto_clearcache_job():
    """Background job: silently clean old files every 30 min."""
    try:
        report = await do_clearcache(force=False)
        from SHUKLAMUSIC.logging import LOGGER
        LOGGER("AutoClean").info(report.replace("**", "").replace("`", ""))
    except Exception as e:
        pass


def start_autoclear_scheduler():
    if not _scheduler.running:
        _scheduler.add_job(
            _auto_clearcache_job,
            trigger="interval",
            minutes=30,
            id="auto_clearcache",
            replace_existing=True,
        )
        _scheduler.start()
