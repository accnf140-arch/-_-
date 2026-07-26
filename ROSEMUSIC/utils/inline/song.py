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
from pyrogram.types import InlineKeyboardButton
from pyrogram.enums import ButtonStyle


def song_markup(_, vidid):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["SG_B_2"],
                callback_data=f"song_helper audio|{vidid}",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text=_["SG_B_3"],
                callback_data=f"song_helper video|{vidid}",
                style=ButtonStyle.SUCCESS,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
                style=ButtonStyle.DANGER,
            ),
        ],
    ]
    return buttons
