# ROSE X MUSIC — Telegram Voice Chat Music Bot

A Python-based Telegram Voice Chat music bot with YouTube, Spotify, SoundCloud support, AI chatbot, playlist management, and much more.

## How to run

The bot starts automatically via the **Start application** workflow (`python run.py`).

It launches:
1. A lightweight HTTP health-check server on port 8000
2. The Telegram bot + assistant userbot (Pyrogram + PyTgCalls)

## Required secrets (all set as Replit Secrets)

| Secret | Description |
|--------|-------------|
| `API_ID` | Telegram API ID from https://my.telegram.org |
| `API_HASH` | Telegram API Hash from https://my.telegram.org |
| `BOT_TOKEN` | Bot token from @BotFather |
| `MONGO_DB_URI` | MongoDB connection string (e.g. MongoDB Atlas) |
| `LOGGER_ID` | Telegram chat/channel ID for bot logs |
| `OWNER_ID` | Your Telegram user ID |
| `STRING_SESSION` | Pyrogram string session for the assistant account |

Optional extras (in `config.py`): `STRING_SESSION2`–`STRING_SESSION7` for multiple assistants, `GROQ_API_KEY` for AI chat, `SPOTIFY_CLIENT_ID`/`SPOTIFY_CLIENT_SECRET`, etc.

## Project structure

```
ROSEMUSIC/          # Main package (also symlinked as SHUKLAMUSIC/)
  __init__.py       # App init: bot client, userbot, platform APIs
  __main__.py       # Entry point: starts bot, loads plugins, registers commands
  core/             # Core components (bot client, call engine, userbot, mongo, git)
  plugins/          # Feature plugins (admins, bot, extra, misc, play, sudo, tools)
  platforms/        # Platform APIs (YouTube, Spotify, SoundCloud, Apple Music, etc.)
  utils/            # Utilities (database helpers, formatters, thumbnails, etc.)
  mongo/            # MongoDB collection helpers
config.py           # All configuration, loaded from environment variables
run.py              # Top-level entry: health server + bot runner
strings/            # Internationalisation strings
```

## Notes

- The package directory is `ROSEMUSIC/` but all internal imports use `SHUKLAMUSIC` — a symlink `SHUKLAMUSIC -> ROSEMUSIC` is present to satisfy this.
- `ROSEMUSIC/plugins/__init__.py` defines `ALL_MODULES` (list of all plugin sub-modules to auto-load).

## User preferences

- Keep the existing project structure and naming conventions.
