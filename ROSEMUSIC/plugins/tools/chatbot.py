# -----------------------------------------------
# 🔸 Rose X Music Project — AI ChatBot v2.0
# 🔹 Groq LLM-powered human-like auto-reply
#    with keyword fallback & human-sensor filtering
# -----------------------------------------------
import asyncio
import random
import re
import time
from pyrogram import filters
from pyrogram.types import Message
from SHUKLAMUSIC import app
from SHUKLAMUSIC.core.mongo import mongodb
from SHUKLAMUSIC.utils.database import is_nonadmin_chat
from SHUKLAMUSIC.misc import SUDOERS
from config import BANNED_USERS, OWNER_ID, GROQ_API_KEY

chatbot_settings = mongodb.chatbot_settings
chatbot_replies   = mongodb.chatbot_replies

_E_ON    = 6073371665381724173   # 🥰
_E_OFF   = 6073598306510967017   # 🐈
_E_LEARN = 6073117703965511893   # 💐
_E_ERR   = 5978715546865112655   # 🚩
_E_AI    = 5931472421780288122   # 🤖

def e(eid, fb):
    return f"<emoji id={eid}>{fb}</emoji>"

# ── Per-chat rate limit: max 1 AI reply every N seconds ──────────────────────
_last_reply: dict[int, float] = {}
_RATE_LIMIT_SEC = 4   # minimum seconds between AI replies in same chat

# ── Messages that are "noise" and should be skipped ──────────────────────────
_SKIP_EXACT = {
    "ok", "okay", "k", "lol", "lmao", "haha", "hahaha", "xd", "😂", "👍",
    "🙏", "❤️", "🔥", "nice", "wow", "yep", "nope", "hmm", "oof", "bruh",
    "yes", "no", "hi", "hello", "hey", "bye", "byee", "thanks", "thank you",
    "ty", "np", "welcome", "sure", "fine", "good", "great", "cool", "👌",
}

_SKIP_PATTERNS = [
    r"^[🔥❤️💯✅👍👎😂😭😅😍😎🥰🤣]+$",   # only emojis
    r"^\.+$",                                  # just dots
    r"^\d+$",                                  # just numbers
    r"^[a-z]{1}$",                             # single letter
]

# ── System prompt: behaves like a friendly human group member ─────────────────
_SYSTEM_PROMPT = """You are a friendly, witty human member in a Telegram group chat.
Rules you MUST follow:
- Reply in the SAME language the user messaged in (Hindi → Hindi, English → English, Hinglish → Hinglish).
- Keep replies SHORT (1–3 sentences max). You are chatting, not writing essays.
- Sound like a real human — casual, natural, sometimes funny. Never say you are an AI or bot.
- If someone asks about music, help them. If they ask general questions, answer helpfully.
- Do NOT use markdown formatting like **bold** or *italic* — plain text only.
- Do NOT start every reply with "Hey" or "Hi". Vary your openings.
- If the message is a greeting, reply warmly and briefly.
- If the message is unclear or too vague, ask a short follow-up question.
- Never generate harmful, sexual, or abusive content."""

CB_HELP = f"""
{e(_E_AI,'🤖')} <b>AI ChatBot — Command List</b>

Powered by Groq AI (LLaMA 3) — responds like a real human in your group language.

• <code>/chatbot on</code>  — enable AI auto-replies in this chat
• <code>/chatbot off</code> — disable AI auto-replies in this chat
• <code>/teach &lt;keyword&gt; | &lt;reply&gt;</code> — teach a custom keyword reply (admin only)
• <code>/unlearn &lt;keyword&gt;</code> — remove a keyword reply (admin only)
• <code>/learned</code> — list all custom keyword replies in this chat
• <code>/chatbothelp</code> — show this help

<i>Custom keyword replies are checked first. If no match, AI generates a human-like response.</i>
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

async def is_chatbot_enabled(chat_id: int) -> bool:
    doc = await chatbot_settings.find_one({"chat_id": chat_id})
    return bool(doc and doc.get("enabled"))


async def set_chatbot_enabled(chat_id: int, enabled: bool):
    await chatbot_settings.update_one(
        {"chat_id": chat_id}, {"$set": {"enabled": enabled}}, upsert=True
    )


async def is_admin(client, message: Message) -> bool:
    if message.sender_chat and message.sender_chat.id == message.chat.id:
        return True
    if not message.from_user:
        return False
    uid = message.from_user.id
    try:
        if uid in SUDOERS or str(uid) == str(OWNER_ID):
            return True
    except Exception:
        pass
    try:
        from pyrogram.enums import ChatMemberStatus
        member = await client.get_chat_member(message.chat.id, uid)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False


def _is_noise(text: str) -> bool:
    """Return True if the message is too short/trivial to reply to."""
    t = text.strip().lower()
    if t in _SKIP_EXACT:
        return True
    for pat in _SKIP_PATTERNS:
        if re.fullmatch(pat, t):
            return True
    # very short non-question
    if len(t) <= 3 and "?" not in t:
        return True
    return False


def _should_reply_randomly() -> bool:
    """Occasionally skip a message to feel more human (not reply to everything)."""
    return random.random() < 0.85   # 85% chance to reply


async def _get_ai_reply(user_text: str) -> str | None:
    """Call Groq API and return the AI response, or None on failure."""
    if not GROQ_API_KEY:
        return None
    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=GROQ_API_KEY)
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",   "content": user_text},
            ],
            max_tokens=150,
            temperature=0.85,
        )
        reply = response.choices[0].message.content.strip()
        return reply if reply else None
    except Exception:
        return None


async def _get_keyword_reply(chat_id: int, text: str) -> str | None:
    """Check MongoDB for a matching keyword reply."""
    text_clean = re.sub(r"[^\w\s]", "", text.lower())
    doc = await chatbot_replies.find_one({"chat_id": chat_id, "keyword": text.lower()})
    if not doc:
        doc = await chatbot_replies.find_one({"chat_id": chat_id, "keyword": text_clean})
    if not doc:
        async for candidate in chatbot_replies.find({"chat_id": chat_id}):
            kw = candidate["keyword"]
            if kw in text_clean.split() or kw in text_clean:
                doc = candidate
                break
    return doc["reply"] if doc else None


# ── Commands ──────────────────────────────────────────────────────────────────

@app.on_message(filters.command("chatbothelp") & ~BANNED_USERS)
async def chatbot_help_cmd(client, message: Message):
    await message.reply_text(CB_HELP)


@app.on_message(filters.command("chatbot") & filters.group & ~BANNED_USERS)
async def chatbot_toggle_cmd(client, message: Message):
    if len(message.command) != 2 or message.command[1].lower() not in ("on", "off"):
        state  = await is_chatbot_enabled(message.chat.id)
        ai_tag = f" {e(_E_AI,'🤖')} <i>AI mode</i>" if GROQ_API_KEY else " <i>(keyword mode — set GROQ_API_KEY for AI)</i>"
        status = f"{e(_E_ON,'🥰')} <b>ON</b>" if state else f"{e(_E_OFF,'🐈')} <b>OFF</b>"
        return await message.reply_text(
            f"{e(_E_LEARN,'💐')} <b>ChatBot status:</b> {status}{ai_tag}\n\n"
            f"Usage: <code>/chatbot on</code> or <code>/chatbot off</code>"
        )
    if not await is_admin(client, message):
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Only group admins can toggle the chatbot.")
    state = message.command[1].lower() == "on"
    await set_chatbot_enabled(message.chat.id, state)
    if state:
        mode = f"{e(_E_AI,'🤖')} AI mode (Groq LLaMA 3)" if GROQ_API_KEY else "keyword mode (set GROQ_API_KEY for AI)"
        await message.reply_text(
            f"{e(_E_ON,'🥰')} <b>ChatBot enabled</b> — running in {mode}.\n"
            f"I will reply to group messages like a real human. 🧠"
        )
    else:
        await message.reply_text(f"{e(_E_OFF,'🐈')} <b>ChatBot disabled</b> for this chat.")


@app.on_message(filters.command("teach") & filters.group & ~BANNED_USERS)
async def teach_cmd(client, message: Message):
    if not await is_admin(client, message):
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Only group admins can teach the chatbot.")
    if len(message.command) < 2 or "|" not in message.text:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Usage: <code>/teach keyword | reply text</code>")
    raw = message.text.split(None, 1)[1]
    if "|" not in raw:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Usage: <code>/teach keyword | reply text</code>")
    keyword, reply = raw.split("|", 1)
    keyword, reply = keyword.strip().lower(), reply.strip()
    if not keyword or not reply:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Both keyword and reply are required.")
    await chatbot_replies.update_one(
        {"chat_id": message.chat.id, "keyword": keyword},
        {"$set": {"reply": reply}},
        upsert=True,
    )
    await message.reply_text(
        f"{e(_E_LEARN,'💐')} Learned! When someone says <b>{keyword}</b>, I'll reply with that."
    )


@app.on_message(filters.command("unlearn") & filters.group & ~BANNED_USERS)
async def unlearn_cmd(client, message: Message):
    if not await is_admin(client, message):
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Only group admins can do this.")
    if len(message.command) < 2:
        return await message.reply_text(f"{e(_E_ERR,'🚩')} Usage: <code>/unlearn keyword</code>")
    keyword = message.text.split(None, 1)[1].strip().lower()
    result = await chatbot_replies.delete_one({"chat_id": message.chat.id, "keyword": keyword})
    if result.deleted_count:
        await message.reply_text(f"{e(_E_ON,'🥰')} Forgot the reply for <b>{keyword}</b>.")
    else:
        await message.reply_text(f"{e(_E_ERR,'🚩')} No learned reply found for that keyword.")


@app.on_message(filters.command("learned") & filters.group & ~BANNED_USERS)
async def learned_cmd(client, message: Message):
    cursor = chatbot_replies.find({"chat_id": message.chat.id}).limit(50)
    keywords = [doc["keyword"] async for doc in cursor]
    if not keywords:
        return await message.reply_text(
            "No custom keyword replies taught yet. Use /teach to add some."
        )
    text = (
        f"{e(_E_LEARN,'💐')} <b>Custom keyword replies in this chat:</b>\n\n"
        + ", ".join(f"<code>{k}</code>" for k in keywords)
    )
    await message.reply_text(text)


# ── Main auto-reply handler ───────────────────────────────────────────────────

@app.on_message(
    filters.group
    & filters.text
    & ~filters.bot
    & ~filters.command(["teach", "unlearn", "learned", "chatbot", "chatbothelp"])
    & ~BANNED_USERS,
    group=20,
)
async def chatbot_auto_reply(client, message: Message):
    if not message.text or message.text.startswith("/"):
        return
    if not await is_chatbot_enabled(message.chat.id):
        return

    text = message.text.strip()

    # ── 1. Always check keyword replies first (instant, no AI cost) ──────────
    keyword_reply = await _get_keyword_reply(message.chat.id, text)
    if keyword_reply:
        try:
            # Small human-like delay even for keyword replies
            await asyncio.sleep(random.uniform(0.4, 1.0))
            await message.reply_text(keyword_reply)
        except Exception:
            pass
        return

    # ── 2. Human sensor — decide whether to even attempt an AI reply ─────────
    if _is_noise(text):
        return

    if not _should_reply_randomly():
        return   # skip ~15% of messages like a real human would

    # ── 3. Rate limit — avoid flooding the group ──────────────────────────────
    now = time.time()
    last = _last_reply.get(message.chat.id, 0)
    if now - last < _RATE_LIMIT_SEC:
        return
    _last_reply[message.chat.id] = now

    # ── 4. Show typing indicator while AI thinks ──────────────────────────────
    try:
        await client.send_chat_action(message.chat.id, "typing")
    except Exception:
        pass

    # ── 5. Human-like thinking delay (0.8 – 2.5 s, proportional to msg length)
    think_time = min(0.8 + len(text) * 0.012, 2.5)
    think_time += random.uniform(-0.2, 0.4)
    await asyncio.sleep(max(0.5, think_time))

    # ── 6. Get AI reply ───────────────────────────────────────────────────────
    reply = await _get_ai_reply(text)

    if not reply:
        # No AI key or API failed — silently skip (don't spam an error)
        return

    try:
        await message.reply_text(reply)
    except Exception:
        pass
