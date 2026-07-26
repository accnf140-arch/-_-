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
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from config import *
from SHUKLAMUSIC import app
from SHUKLAMUSIC.core.call import SHUKLA
from SHUKLAMUSIC.utils import bot_sys_stats
from SHUKLAMUSIC.utils.decorators.language import language
from SHUKLAMUSIC.utils.inline import supp_markup
from config import BANNED_USERS, PING_IMG_URL
import random

# Always show this thumbnail on ping
_PING_THUMB = "https://i.ibb.co/TMfqTY3f/rose-thumb.jpg"

@app.on_message(filters.command("ping", prefixes=["/"]) & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    start = datetime.now()
    # Send photo with the Rose thumbnail and loading caption
    try:
        response = await message.reply_photo(
            _PING_THUMB,
            caption=_["ping_1"].format(app.mention),
        )
    except Exception:
        # Fallback: if ibb URL fails, use PING_IMG_URL from config
        try:
            response = await message.reply_photo(
                PING_IMG_URL,
                caption=_["ping_1"].format(app.mention),
            )
        except Exception:
            response = await message.reply_text(_["ping_1"].format(app.mention))

    pytgping = await SHUKLA.ping()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    resp = (datetime.now() - start).microseconds / 1000
    try:
        await response.edit_caption(
            _["ping_2"].format(resp, app.mention, UP, RAM, CPU, DISK, pytgping),
            reply_markup=supp_markup(_),
        )
    except Exception:
        await response.edit_text(
            _["ping_2"].format(resp, app.mention, UP, RAM, CPU, DISK, pytgping),
            reply_markup=supp_markup(_),
        )
