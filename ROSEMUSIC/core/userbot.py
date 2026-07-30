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
from pyrogram import Client
import config
from ..logging import LOGGER

assistants = []
assistantids = []


class Userbot(Client):
    def __init__(self):
        self.one = Client(
            name="SHUKLAAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
            no_updates=True,
        )
        self.two = Client(
            name="SHUKLAAss2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
            no_updates=True,
        )
        self.three = Client(
            name="SHUKLAAss3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
            no_updates=True,
        )
        self.four = Client(
            name="SHUKLAAss4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
            no_updates=True,
        )
        self.five = Client(
            name="SHUKLAAss5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
            no_updates=True,
        )

    async def _start_one(self, client, number: int):
        """Start a single assistant client, skipping gracefully on session errors."""
        label = f"Assistant {number}"
        try:
            await client.start()
        except Exception as e:
            err_str = str(e)
            err_name = type(e).__name__
            # AUTH_KEY_DUPLICATED — same session already running elsewhere
            if "AuthKeyDuplicated" in err_name or "AUTH_KEY_DUPLICATED" in err_str:
                LOGGER(__name__).warning(
                    f"{label}: AUTH_KEY_DUPLICATED — session is already active on another "
                    f"instance. Skipping this assistant. Stop the other instance or generate "
                    f"a fresh STRING_SESSION."
                )
            else:
                LOGGER(__name__).error(f"{label} failed to start: {type(e).__name__}: {e}")
            return False

        try:
            await client.join_chat("ITSZSHUKLA")
        except Exception:
            pass

        assistants.append(number)
        try:
            await client.send_message(config.LOGGER_ID, f"{label} Started")
        except Exception:
            LOGGER(__name__).warning(
                f"{label} could not message log group — make sure it is added as admin."
            )

        client.id = client.me.id
        client.name = client.me.mention
        client.username = client.me.username
        assistantids.append(client.id)
        LOGGER(__name__).info(f"{label} Started as {client.name}")
        return True

    async def start(self):
        LOGGER(__name__).info("Starting Assistants...")
        pairs = [
            (self.one,   1, config.STRING1),
            (self.two,   2, config.STRING2),
            (self.three, 3, config.STRING3),
            (self.four,  4, config.STRING4),
            (self.five,  5, config.STRING5),
        ]
        started = 0
        for client, number, string_val in pairs:
            if string_val:
                ok = await self._start_one(client, number)
                if ok:
                    started += 1

        if started == 0:
            LOGGER(__name__).warning(
                "⚠️ No assistants started — STRING_SESSION may be duplicated (running on two "
                "servers) or expired. Voice-chat features will be unavailable until a valid "
                "session is set. Generate a new one with @StringFatherBot and update "
                "STRING_SESSION in your environment variables."
            )

    async def stop(self):
        LOGGER(__name__).info("Stopping Assistants...")
        pairs = [
            (self.one,   1, config.STRING1),
            (self.two,   2, config.STRING2),
            (self.three, 3, config.STRING3),
            (self.four,  4, config.STRING4),
            (self.five,  5, config.STRING5),
        ]
        for client, number, string_val in pairs:
            if not string_val:
                continue
            try:
                await client.stop()
            except Exception as e:
                LOGGER(__name__).warning(
                    f"Assistant {number} did not stop cleanly: {type(e).__name__}: {e}"
                )
