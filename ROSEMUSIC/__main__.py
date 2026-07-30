# -----------------------------------------------
# SHUKLAMUSIC / ROSE X MUSIC Bot — entry point
# -----------------------------------------------
import asyncio
import importlib
import os
from aiohttp import web
from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall
import config
from SHUKLAMUSIC import LOGGER, app, userbot
from SHUKLAMUSIC.core.call import SHUKLA
from SHUKLAMUSIC.misc import sudo
from SHUKLAMUSIC.plugins import ALL_MODULES
from SHUKLAMUSIC.utils.database import get_banned_users, get_gbanned
from SHUKLAMUSIC.plugins.tools.vclogger import initialize_vc_logger
from SHUKLAMUSIC.core.commands import register_bot_commands
from SHUKLAMUSIC.plugins.sudo.clearcache import start_autoclear_scheduler


# ── Keep-alive web server ─────────────────────────────────────────────────────
async def _ping(request):
    return web.Response(text="OK")


async def start_keepalive():
    """Start a lightweight HTTP server so the repl stays alive via pings."""
    _app = web.Application()
    _app.router.add_get("/", _ping)
    _app.router.add_get("/ping", _ping)
    runner = web.AppRunner(_app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    LOGGER("SHUKLAMUSIC").info(f"Keep-alive server started on port {port}")


async def init():
    if not any([config.STRING1, config.STRING2, config.STRING3,
                config.STRING4, config.STRING5]):
        LOGGER(__name__).error(
            "No STRING_SESSION found. Please set STRING_SESSION in your environment variables."
        )
        raise SystemExit(1)

    await sudo()

    # Pre-load ban lists into memory (failures are non-fatal)
    try:
        await get_gbanned()
        await get_banned_users()
    except Exception as e:
        LOGGER(__name__).warning(f"Could not load ban lists: {e}")

    await app.start()

    for all_module in ALL_MODULES:
        importlib.import_module("SHUKLAMUSIC.plugins" + all_module)
    LOGGER("SHUKLAMUSIC.plugins").info("All Features Loaded!")

    await register_bot_commands()
    await userbot.start()
    await SHUKLA.start()

    # Optional startup stream in the log group (non-fatal if it fails)
    try:
        await SHUKLA.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("SHUKLAMUSIC").warning(
            "No active voice chat in LOGGER_ID — skipping startup audio."
        )
    except Exception as e:
        LOGGER("SHUKLAMUSIC").warning(f"Startup stream skipped: {type(e).__name__}: {e}")

    await SHUKLA.decorators()
    await initialize_vc_logger()
    start_autoclear_scheduler()
    LOGGER("SHUKLAMUSIC").info("Auto-clean scheduler started (every 30 min).")
    await start_keepalive()
    LOGGER("SHUKLAMUSIC").info("Bot fully started!")
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("SHUKLAMUSIC").info("Bot stopped.")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
