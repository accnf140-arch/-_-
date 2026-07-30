# -----------------------------------------------
# 🔸 Rose X Music Project
# 🔹 Developed & Maintained by: Rose X Music (https://t.me/rosexupdates)
# 📅 Copyright © 2022 – All Rights Reserved
#
# 📖 License:
# This source code is open for educational and non-commercial use ONLY.
# You are required to retain this credit in all copies or substantial portions of this file.
# Commercial use, redistribution, or removal of this notice is strictly prohibited
# without prior written permission from the author.
#
# ❤️ Made with ❤️ for Rose X Music Community
# -----------------------------------------------
# NOTE: The Call class lives exclusively in core/call.py.
#       This module only registers bot commands with Telegram.
# -----------------------------------------------


async def register_bot_commands():
    """Register the bot command list visible in Telegram's command menu."""
    from pyrogram.types import BotCommand
    from SHUKLAMUSIC import app, LOGGER

    commands = [
        BotCommand("start",   "Start the bot"),
        BotCommand("help",    "Get help"),
        BotCommand("play",    "Play a song"),
        BotCommand("vplay",   "Play a video"),
        BotCommand("stop",    "Stop playback"),
        BotCommand("pause",   "Pause playback"),
        BotCommand("resume",  "Resume playback"),
        BotCommand("skip",    "Skip current song"),
        BotCommand("queue",   "Show queue"),
        BotCommand("end",     "End the stream"),
        BotCommand("ping",    "Check bot latency"),
        BotCommand("song",    "Download a song"),
        BotCommand("search",  "Search YouTube"),
        BotCommand("lyrics",  "Get lyrics"),
        BotCommand("stats",   "Bot statistics"),
    ]
    try:
        await app.set_bot_commands(commands)
        LOGGER(__name__).info("Bot commands registered successfully.")
    except Exception as e:
        LOGGER(__name__).warning(f"Could not register bot commands: {e}")
