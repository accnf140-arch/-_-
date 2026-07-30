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

import sys

# Optional uvloop — faster event loop on Linux
if sys.platform != "win32":
    try:
        import uvloop
        uvloop.install()
        print("✓ uvloop enabled")
    except ImportError:
        print("⚠ uvloop not installed, using default asyncio loop")

from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus
import config
from ..logging import LOGGER


class SHUKLA(Client):
    def __init__(self):
        LOGGER(__name__).info("Starting Bot...")

        super().__init__(
            name="ROSE X MUSIC",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        import asyncio as _asyncio
        from pyrogram.errors import FloodWait as _FloodWait
        for _attempt in range(5):
            try:
                await super().start()
                break
            except _FloodWait as fw:
                wait = fw.value + 5
                LOGGER(__name__).warning(
                    f"Telegram FloodWait on bot auth — waiting {wait}s before retry "
                    f"(attempt {_attempt + 1}/5)…"
                )
                await _asyncio.sleep(wait)

        me = await self.get_me()

        self.id = me.id
        self.name = f"{me.first_name} {me.last_name or ''}".strip()
        self.username = me.username or "None"
        self.mention = me.mention

        # Send startup notification to the log group
        try:
            await self.send_message(
                chat_id=config.LOGGER_ID,
                text=(
                    f"<u><b>» {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b></u>\n\n"
                    f"ɪᴅ : <code>{self.id}</code>\n"
                    f"ɴᴀᴍᴇ : {self.name}\n"
                    f"ᴜsᴇʀɴᴀᴍᴇ : @{self.username}"
                ),
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error(
                "Bot cannot access LOGGER_ID. Add the bot to the log group/channel first."
            )
            raise SystemExit(1)
        except Exception as ex:
            LOGGER(__name__).error(
                f"Failed to send startup message to LOGGER_ID: {type(ex).__name__}: {ex}"
            )
            raise SystemExit(1)

        # Verify bot has admin rights in the log group
        try:
            member = await self.get_chat_member(config.LOGGER_ID, self.id)
            if member.status not in (
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER,
            ):
                LOGGER(__name__).error(
                    "Bot is not an admin in LOGGER_ID. Promote it to admin and restart."
                )
                raise SystemExit(1)
        except SystemExit:
            raise
        except (errors.ChatAdminRequired, errors.UserNotParticipant):
            LOGGER(__name__).error(
                "Bot is not a member/admin of LOGGER_ID. Add it as admin and restart."
            )
            raise SystemExit(1)
        except Exception as ex:
            # get_chat_member can fail for broadcast channels — that's acceptable
            LOGGER(__name__).warning(
                f"Could not verify admin status in LOGGER_ID "
                f"({type(ex).__name__}: {ex}) — continuing."
            )

        LOGGER(__name__).info(
            f"Music Bot Started Successfully as {self.name}"
        )

    async def stop(self):
        LOGGER(__name__).info("Stopping Bot...")
        await super().stop()
