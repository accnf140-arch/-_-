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
import random, os
from pyrogram import Client, filters, enums 
from SHUKLAMUSIC import app
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


@app.on_message(filters.command(["genpassword", 'genpw']))
async def password(bot, update):
    message = await update.reply_text(text="Pʀᴏᴄᴇꜱꜱɪɴɢ..")
    password = "abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()_+".lower()
    if len(update.command) > 1:
        qw = update.text.split(" ", 1)[1]
    else:
        ST = ["5", "7", "6", "9", "10", "12", "14", "8", "13"] 
        qw = random.choice(ST)
    limit = int(qw)
    random_value = "".join(random.sample(password, limit))
    txt = f"<b>Lɪᴍɪᴛ:</b> {str(limit)} \n<b>Pᴀꜱꜱᴡᴏʀᴅ: <code>{random_value}</code>"
    btn = InlineKeyboardMarkup([[InlineKeyboardButton('𝗔𝗗𝗗 𝗠𝗘', url='https://t.me/SapnaMusicRobot?startgroup=true')]])
    await message.edit_text(text=txt, reply_markup=btn, parse_mode=enums.ParseMode.HTML)
