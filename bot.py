# bot.py — Telegram bot (pyTelegramBotAPI)
import logging
import threading

import telebot
from telebot.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import ADMIN_ID, BOT_TOKEN
from database import (
    add_channel,
    add_subscriber,
    get_channels,
    get_subscribers,
    remove_subscriber,
    set_channels,
)
from monitor import resolve_channel, start_monitor

logger = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Admin holati: {user_id: "add" | "broadcast"}
_state: dict = {}


# ═══════════════════════════════════════
# BROADCAST
# ═══════════════════════════════════════

def broadcast(text: str):
    ok = fail = 0
    for uid in get_subscribers():
        try:
            bot.send_message(uid, text, parse_mode="HTML", disable_web_page_preview=False)
            ok += 1
        except Exception as exc:
            logger.warning(f"Yuborilmadi {uid}: {exc}")
            fail += 1
    return ok, fail


# ═══════════════════════════════════════
# FOYDALANUVCHI BUYRUQLARI
# ═══════════════════════════════════════

@bot.message_handler(commands=["start"])
def cmd_start(message: Message):
    is_new = add_subscriber(message.from_user.id)
    if is_new:
        text = (
            "👋 <b>Assalomu alaykum!</b>\n\n"
            "🎬 Siz quyidagi YouTube kanallarning yangi videolaridan "
            "<b>avtomatik xabar</b> olasiz:\n\n"
            "• 🤖 AI Master\n"
            "• 💼 Azizbek Baxodirov\n"
            "• 🧠 Neurobatya\n"
            "• ⚡ Xondamir Xolmurodov\n\n"
            "✅ <b>Obuna bo'ldingiz!</b>\n"
            "❌ Chiqish: /unsubscribe"
        )
    else:
        text = (
            "✅ <b>Siz allaqachon obuna bo'lgansiz!</b>\n\n"
            "📡 Yangi video chiqqanda xabar olasiz.\n"
            "❌ Chiqish: /unsubscribe"
        )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=["unsubscribe"])
def cmd_unsubscribe(message: Message):
    if remove_subscriber(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Obuna bekor qilindi.\nQaytish: /start")
    else:
        bot.send_message(message.chat.id, "Siz obuna emassiz. /start yozing.")


# ═══════════════════════════════════════
# ADMIN PANEL
# ═══════════════════════════════════════

def admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton("📋 Kanallar", callback_data="a_list"))
    kb.row(
        InlineKeyboardButton("➕ Qo'shish", callback_data="a_add"),
        InlineKeyboardButton("🗑️ O'chirish", callback_data="a_remove"),
    )
    kb.row(
        InlineKeyboardButton("👥 Obunachlar", callback_data="a_users"),
        InlineKeyboardButton("📣 Xabar yuborish", callback_data="a_broadcast"),
    )
    return kb


@bot.message_handler(commands=["admin"])
def cmd_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "🚫 Faqat admin uchun.")
        return
    bot.send_message(
        message.chat.id,
        "🛠️ <b>Admin Panel</b>",
        reply_markup=admin_kb(),
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("a_") or c.data.startswith("del_"))
def handle_cb(cb: CallbackQuery):
    uid = cb.from_user.id
    if uid != ADMIN_ID:
        bot.answer_callback_query(cb.id, "🚫 Ruxsat yo'q!")
        return

    d = cb.data
    cid = cb.message.chat.id
    mid = cb.message.message_id

    # ── Kanallar ro'yxati ──
    if d == "a_list":
        chans = get_channels()
        body = "\n".join(f"{i+1}. <code>{c}</code>" for i, c in enumerate(chans)) if chans else "Bo'sh"
        bot.edit_message_text(f"📋 <b>Kanallar:</b>\n\n{body}", cid, mid, reply_markup=admin_kb())

    # ── Obunachlar soni ──
    elif d == "a_users":
        count = len(get_subscribers())
        bot.edit_message_text(f"👥 <b>Obunachlar:</b> {count} ta", cid, mid, reply_markup=admin_kb())

    # ── Kanal qo'shish ──
    elif d == "a_add":
        _state[uid] = "add"
        back = InlineKeyboardMarkup()
        back.row(InlineKeyboardButton("🔙 Orqaga", callback_data="a_back"))
        bot.edit_message_text(
            "➕ Kanal URL ni yuboring:\n<code>https://www.youtube.com/@kanal_nomi</code>",
            cid, mid, reply_markup=back,
        )

    # ── Kanal o'chirish ──
    elif d == "a_remove":
        chans = get_channels()
        if not chans:
            bot.answer_callback_query(cb.id, "Ro'yxat bo'sh!", show_alert=True)
            return
        kb = InlineKeyboardMarkup()
        for i, url in enumerate(chans):
            label = url.split("@")[-1][:35]
            kb.row(InlineKeyboardButton(f"🗑️ @{label}", callback_data=f"del_{i}"))
        kb.row(InlineKeyboardButton("🔙 Orqaga", callback_data="a_back"))
        bot.edit_message_text("O'chirmoqchi bo'lgan kanalni tanlang:", cid, mid, reply_markup=kb)

    # ── Kanal o'chirish (tanlanganda) ──
    elif d.startswith("del_"):
        idx = int(d.split("_")[1])
        chans = get_channels()
        if idx < len(chans):
            removed = chans.pop(idx)
            set_channels(chans)
            bot.edit_message_text(f"✅ O'chirildi:\n<code>{removed}</code>", cid, mid, reply_markup=admin_kb())

    # ── Broadcast ──
    elif d == "a_broadcast":
        _state[uid] = "broadcast"
        back = InlineKeyboardMarkup()
        back.row(InlineKeyboardButton("🔙 Orqaga", callback_data="a_back"))
        bot.edit_message_text("📣 Barcha obunachilarga yuboriladigan xabarni yozing:", cid, mid, reply_markup=back)

    # ── Orqaga ──
    elif d == "a_back":
        _state.pop(uid, None)
        bot.edit_message_text("🛠️ <b>Admin Panel</b>", cid, mid, reply_markup=admin_kb())

    bot.answer_callback_query(cb.id)


@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and _state.get(m.from_user.id))
def handle_admin_input(message: Message):
    uid = message.from_user.id
    state = _state.pop(uid, None)

    if state == "add":
        url = message.text.strip()
        bot.send_message(message.chat.id, "⏳ Tekshirilmoqda...")
        try:
            meta = resolve_channel(url)
        except Exception as exc:
            bot.send_message(message.chat.id, f"❌ Topilmadi: {exc}", reply_markup=admin_kb())
            return
        if add_channel(url):
            bot.send_message(
                message.chat.id,
                f"✅ Kanal qo'shildi!\n👤 <b>{meta['uploader']}</b>",
                reply_markup=admin_kb(),
            )
        else:
            bot.send_message(message.chat.id, "⚠️ Bu kanal allaqachon bor.", reply_markup=admin_kb())

    elif state == "broadcast":
        ok, fail = broadcast(message.text)
        bot.send_message(
            message.chat.id,
            f"📣 Yuborildi: ✅ {ok} ta | ❌ {fail} ta",
            reply_markup=admin_kb(),
        )


# ═══════════════════════════════════════
# YANGI VIDEO CALLBACK
# ═══════════════════════════════════════

def on_new_video(data: dict):
    text = (
        f"🎬 <b>{data['owner_name']}</b> kanalida yangi video!\n\n"
        f"📌 <b>{data['title']}</b>\n\n"
        f"📝 <i>{data['summary']}</i>\n\n"
        f"▶️ <a href=\"{data['url']}\">Videoni ko'rish</a>"
    )
    ok, fail = broadcast(text)
    logger.info(f"Xabar yuborildi: {ok} ✅  {fail} ❌")


# ═══════════════════════════════════════
# BOT ISHGA TUSHIRISH
# ═══════════════════════════════════════

def run_bot():
    logger.info("Telegram polling boshlanmoqda...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
