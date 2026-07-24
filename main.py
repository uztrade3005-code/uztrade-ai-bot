import os
import sqlite3
import logging
import asyncio
from datetime import datetime, timezone
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
# ============================================================
# НАСТРОЙКИ
# ============================================================
BOT_TOKEN = os.getenv("8993152771:AAFWxb-VdsM3xPrH00BHOc-1-j-ozbAlh_w")
ADMIN_ID = int(os.getenv("7962666075", "0"))
DB_FILE = os.getenv("DB_FILE", "uztrade_users.db")
OPERATOR_USERNAME = "@uztrade_support"
OPERATOR_URL = "https://t.me/uztrade_support"
# ============================================================
# ЛОГИРОВАНИЕ
# ============================================================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)
# ============================================================
# DATABASE
# ============================================================
def get_db():
    return sqlite3.connect(DB_FILE)
def init_database():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            telegram_first_name TEXT,
            telegram_last_name TEXT,
            name TEXT,
            age TEXT,
            city TEXT,
            phone TEXT,
            created_at TEXT,
            last_seen_at TEXT,
            is_blocked INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    logger.info("UZTRADE database initialized")
# ============================================================
# СОХРАНЕНИЕ ПОЛЬЗОВАТЕЛЯ
# ============================================================
def save_user(user):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        INSERT INTO users (
            telegram_id,
            username,
            telegram_first_name,
            telegram_last_name,
            created_at,
            last_seen_at,
            is_blocked
        )
        VALUES (?, ?, ?, ?, ?, ?, 0)
        ON CONFLICT(telegram_id)
        DO UPDATE SET
            username = excluded.username,
            telegram_first_name = excluded.telegram_first_name,
            telegram_last_name = excluded.telegram_last_name,
            last_seen_at = excluded.last_seen_at
    """, (
        user.id,
        user.username,
        user.first_name,
        user.last_name,
        now,
        now
    ))
    conn.commit()
    conn.close()
# ============================================================
# СОХРАНЕНИЕ ИМЕНИ
# ============================================================
def save_name(telegram_id, name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET name = ?
        WHERE telegram_id = ?
    """, (name, telegram_id))
    conn.commit()
    conn.close()
# ============================================================
# СОХРАНЕНИЕ ВОЗРАСТА
# ============================================================
def save_age(telegram_id, age):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET age = ?
        WHERE telegram_id = ?
    """, (age, telegram_id))
    conn.commit()
    conn.close()
# ============================================================
# СОХРАНЕНИЕ ГОРОДА
# ============================================================
def save_city(telegram_id, city):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET city = ?
        WHERE telegram_id = ?
    """, (city, telegram_id))
    conn.commit()
    conn.close()
# ============================================================
# СОХРАНЕНИЕ ТЕЛЕФОНА
# ============================================================
def save_phone(telegram_id, phone):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET phone = ?
        WHERE telegram_id = ?
    """, (phone, telegram_id))
    conn.commit()
    conn.close()
# ============================================================
# АКТИВНЫЕ ПОЛЬЗОВАТЕЛИ
# ============================================================
def get_active_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT telegram_id
        FROM users
        WHERE is_blocked = 0
    """)
    users = cursor.fetchall()
    conn.close()
    return [user[0] for user in users]
# ============================================================
# СТАТИСТИКА
# ============================================================
def get_user_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE is_blocked = 0
    """)
    active = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE is_blocked = 1
    """)
    blocked = cursor.fetchone()[0]
    conn.close()
    return total, active, blocked
# ============================================================
# БЛОКИРОВКА ПОЛЬЗОВАТЕЛЯ
# ============================================================
def mark_blocked(telegram_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET is_blocked = 1
        WHERE telegram_id = ?
    """, (telegram_id,))
    conn.commit()
    conn.close()
# ============================================================
# ГЛАВНОЕ МЕНЮ
# ============================================================
def main_keyboard():
    keyboard = [
        [
            KeyboardButton("📝 Ro‘yxatdan o‘tish")
        ],
        [
            KeyboardButton("👨‍💼 Operator bilan bog‘lanish")
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )
# ============================================================
# КНОПКА ТЕЛЕФОНА
# ============================================================
def phone_keyboard():
    keyboard = [
        [
            KeyboardButton(
                "📱 Telefon raqamimni yuborish",
                request_contact=True
            )
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
# ============================================================
# КНОПКА ОПЕРАТОРА
# ============================================================
def operator_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "👨‍💼 Operator bilan bog‘lanish",
                url=OPERATOR_URL
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
# ============================================================
# КНОПКА ОПЕРАТОРА ДЛЯ РАССЫЛКИ
# ============================================================
def broadcast_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "👨‍💼 Operator bilan bog‘lanish",
                url=OPERATOR_URL
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
# ============================================================
# /START
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)
    context.user_data.clear()
    await update.message.reply_text(
        "Assalomu alaykum! 👋\n\n"
        "UZTRADE SCHOOL rasmiy botiga "
        "xush kelibsiz! 📈\n\n"
        "Master-klasslar, yangiliklar va "
        "foydali ma'lumotlardan birinchilardan "
        "bo‘lib xabardor bo‘lish uchun "
        "ro‘yxatdan o‘ting. 🔥\n\n"
        "Kerakli bo‘limni tanlang 👇",
        reply_markup=main_keyboard()
    )
# ============================================================
# НАЧАЛО РЕГИСТРАЦИИ
# ============================================================
async def start_registration(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    context.user_data.clear()
    context.user_data["registration"] = True
    context.user_data["step"] = "name"
    await update.message.reply_text(
        "📝 UZTRADE SCHOOL RO‘YXATDAN O‘TISH\n\n"
        "Bepul master-klassimizga ro‘yxatdan "
        "o‘tish uchun ma'lumotlaringizni kiriting. ✅\n\n"
        "1️⃣ Ismingizni yozing:",
        reply_markup=ReplyKeyboardRemove()
    )
# ============================================================
# ОПЕРАТОР
# ============================================================
async def operator(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "👨‍💼 Operator bilan bog‘lanish\n\n"
        "Savollaringiz bo‘lsa, "
        "operatorimiz bilan bog‘lanishingiz mumkin.",
        reply_markup=operator_keyboard()
    )
# ============================================================
# ОБРАБОТКА ТЕКСТА
# ============================================================
async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user = update.effective_user
    text = update.message.text
    # ========================================================
    # ГЛАВНОЕ МЕНЮ
    # ========================================================
    if text == "📝 Ro‘yxatdan o‘tish":
        await start_registration(update, context)
        return
    if text == "👨‍💼 Operator bilan bog‘lanish":
        await operator(update, context)
        return
    # ========================================================
    # РАССЫЛКА
    # ========================================================
    if context.user_data.get("broadcast_mode"):
        if user.id != ADMIN_ID:
            return
        context.user_data["broadcast_text"] = text
        users = get_active_users()
        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Отправить всем",
                    callback_data="confirm_broadcast"
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ Отмена",
                    callback_data="cancel_broadcast"
                )
            ]
        ]
        await update.message.reply_text(
            "📢 PREVIEW РАССЫЛКИ\n\n"
            f"{text}\n\n"
            "━━━━━━━━━━━━━━\n"
            f"👥 Получателей: {len(users)}\n\n"
            "Отправить сообщение всем?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    # ========================================================
    # РЕГИСТРАЦИЯ
    # ========================================================
    if context.user_data.get("registration"):
        step = context.user_data.get("step")
        # ====================================================
        # ИМЯ
        # ====================================================
        if step == "name":
            context.user_data["name"] = text
            save_name(user.id, text)
            context.user_data["step"] = "age"
            await update.message.reply_text(
                "2️⃣ Yoshingizni yozing:"
            )
            return
        # ====================================================
        # ВОЗРАСТ
        # ====================================================
        if step == "age":
            if not text.isdigit():
                await update.message.reply_text(
                    "❌ Iltimos, yoshingizni raqam bilan yozing.\n\n"
                    "Masalan: 22"
                )
                return
            age = int(text)
            if age < 10 or age > 100:
                await update.message.reply_text(
                    "❌ Iltimos, yoshingizni to‘g‘ri kiriting."
                )
                return
            context.user_data["age"] = text
            save_age(user.id, text)
            context.user_data["step"] = "city"
            await update.message.reply_text(
                "3️⃣ Qaysi shahar/tumanda yashaysiz?"
            )
            return
        # ====================================================
        # ГОРОД
        # ====================================================
        if step == "city":
            context.user_data["city"] = text
            save_city(user.id, text)
            context.user_data["step"] = "phone"
            await update.message.reply_text(
                "4️⃣ Telefon raqamingizni yuboring 📱\n\n"
                "Quyidagi tugmani bosing:",
                reply_markup=phone_keyboard()
            )
            return
    # ========================================================
    # НЕИЗВЕСТНОЕ СООБЩЕНИЕ
    # ========================================================
    await update.message.reply_text(
        "Iltimos, menyudan kerakli "
        "bo‘limni tanlang 👇",
        reply_markup=main_keyboard()
    )
# ============================================================
# ОБРАБОТКА ТЕЛЕФОНА
# ============================================================
async def contact_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user = update.effective_user
    contact = update.message.contact
    # ========================================================
    # ПРОВЕРКА ВЛАДЕЛЬЦА НОМЕРА
    # ========================================================
    if contact.user_id != user.id:
        await update.message.reply_text(
            "❌ Iltimos, faqat o‘zingizning "
            "telefon raqamingizni yuboring.\n\n"
            "Quyidagi tugmani bosing 👇",
            reply_markup=phone_keyboard()
        )
        return
    # ========================================================
    # ПРОВЕРКА РЕГИСТРАЦИИ
    # ========================================================
    if not context.user_data.get("registration"):
        await update.message.reply_text(
            "Iltimos, avval ro‘yxatdan o‘ting.",
            reply_markup=main_keyboard()
        )
        return
    if context.user_data.get("step") != "phone":
        return
    # ========================================================
    # ПОЛУЧАЕМ ТЕЛЕФОН
    # ========================================================
    phone = contact.phone_number
    save_phone(user.id, phone)
    context.user_data["phone"] = phone
    # ========================================================
    # ПОЛУЧАЕМ ДАННЫЕ
    # ========================================================
    name = context.user_data.get(
        "name",
        "Noma'lum"
    )
    age = context.user_data.get(
        "age",
        "Noma'lum"
    )
    city = context.user_data.get(
        "city",
        "Noma'lum"
    )
    username = (
        f"@{user.username}"
        if user.username
        else "Username yo‘q"
    )
    # ========================================================
    # УВЕДОМЛЕНИЕ АДМИНИСТРАТОРУ
    # ========================================================
    admin_message = (
        "🆕 YANGI REGISTRATSIYA!\n\n"
        "🏢 UZTRADE SCHOOL\n\n"
        f"👤 Ism: {name}\n"
        f"🎂 Yosh: {age}\n"
        f"📍 Shahar/tuman: {city}\n"
        f"📱 Telefon: {phone}\n\n"
        f"👤 Username: {username}\n"
        f"🆔 Telegram ID: {user.id}"
    )
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message
        )
    except Exception as error:
        logger.error(
            f"Admin notification error: {error}"
        )
    # ========================================================
    # ОЧИЩАЕМ СОСТОЯНИЕ
    # ========================================================
    context.user_data.clear()
    # ========================================================
    # ПОЗДРАВЛЕНИЕ
    # ========================================================
    await update.message.reply_text(
        "🎉 Tabriklaymiz!\n\n"
        "Siz UZTRADE SCHOOL bepul "
        "master-klassiga muvaffaqiyatli "
        "ro‘yxatdan o‘tdingiz! ✅\n\n"
        "Master-klass vaqti hamda barcha "
        "kerakli ma'lumotlar sizga "
        "Telegram orqali yuboriladi. 📩",
        reply_markup=main_keyboard()
    )
# ============================================================
# /BROADCAST
# ============================================================
async def broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text(
            "❌ Sizda ruxsat yo‘q."
        )
        return
    context.user_data["broadcast_mode"] = True
    await update.message.reply_text(
        "📢 UZTRADE RASSYLKA\n\n"
        "Yuboriladigan xabarni yuboring.\n\n"
        "❌ Bekor qilish uchun /cancel yozing."
    )
# ============================================================
# /CANCEL
# ============================================================
async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user = update.effective_user
    if user.id == ADMIN_ID:
        context.user_data.clear()
        await update.message.reply_text(
            "❌ Rassylka bekor qilindi.",
            reply_markup=main_keyboard()
        )
# ============================================================
# /USERS
# ============================================================
async def users_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user = update.effective_user
    if user.id != ADMIN_ID:
        return
    total, active, blocked = get_user_stats()
    await update.message.reply_text(
        "👥 UZTRADE FOYDALANUVCHILARI\n\n"
        f"👥 Jami: {total}\n"
        f"🟢 Faol: {active}\n"
        f"🔴 Bloklagan: {blocked}\n\n"
        f"🆔 Admin ID: {ADMIN_ID}"
    )
# ============================================================
# CALLBACK-КНОПКИ
# ============================================================
async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    # ========================================================
    # ПОДТВЕРЖДЕНИЕ РАССЫЛКИ
    # ========================================================
    if query.data == "confirm_broadcast":
        if query.from_user.id != ADMIN_ID:
            return
        message_text = context.user_data.get(
            "broadcast_text"
        )
        if not message_text:
            await query.edit_message_text(
                "❌ Xabar topilmadi."
            )
            return
        users = get_active_users()
        success = 0
        failed = 0
        blocked = 0
        await query.edit_message_text(
            "📢 Rassylka boshlandi...\n\n"
            f"👥 Jami: {len(users)}"
        )
        for user_id in users:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=message_text,
                    reply_markup=broadcast_keyboard()
                )
                success += 1
                await asyncio.sleep(0.05)
            except Exception as error:
                failed += 1
                error_text = str(error).lower()
                if (
                    "blocked" in error_text
                    or "deactivated" in error_text
                    or "chat not found" in error_text
                ):
                    mark_blocked(user_id)
                    blocked += 1
                logger.error(
                    f"Broadcast error for {user_id}: {error}"
                )
        context.user_data.clear()
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "✅ RASSYLKA YAKUNLANDI!\n\n"
                f"👥 Jami: {len(users)}\n"
                f"📨 Yuborildi: {success}\n"
                f"❌ Xatolik: {failed}\n"
                f"🚫 Bloklaganlar: {blocked}"
            ),
            reply_markup=main_keyboard()
        )
        return
    # ========================================================
    # ОТМЕНА РАССЫЛКИ
    # ========================================================
    if query.data == "cancel_broadcast":
        context.user_data.clear()
        await query.edit_message_text(
            "❌ Rassylka bekor qilindi."
        )
# ============================================================
# ОБРАБОТКА ОШИБОК
# ============================================================
async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):
    logger.error(
        "Exception while handling update:",
        exc_info=context.error
    )
# ============================================================
# MAIN
# ============================================================
def main():
    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN topilmadi. "
            "Railway Variables ga BOT_TOKEN qo‘shing."
        )
    if not ADMIN_ID:
        raise ValueError(
            "ADMIN_ID topilmadi. "
            "Railway Variables ga ADMIN_ID qo‘shing."
        )
    # ========================================================
    # DATABASE
    # ========================================================
    init_database()
    # ========================================================
    # APPLICATION
    # ========================================================
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )
    # ========================================================
    # КОМАНДЫ
    # ========================================================
    application.add_handler(
        CommandHandler("start", start)
    )
    application.add_handler(
        CommandHandler("broadcast", broadcast)
    )
    application.add_handler(
        CommandHandler("users", users_command)
    )
    application.add_handler(
        CommandHandler("cancel", cancel)
    )
    # ========================================================
    # ТЕЛЕФОН
    # ========================================================
    application.add_handler(
        MessageHandler(
            filters.CONTACT,
            contact_handler
        )
    )
    # ========================================================
    # INLINE-КНОПКИ
    # ========================================================
    application.add_handler(
        CallbackQueryHandler(
            callback_handler
        )
    )
    # ========================================================
    # ТЕКСТ
    # ========================================================
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )
    # ========================================================
    # ОШИБКИ
    # ========================================================
    application.add_error_handler(
        error_handler
    )
    logger.info(
        "UZTRADE ASSISTANT BOT IS RUNNING ON RAILWAY..."
    )
    # ========================================================
    # ЗАПУСК
    # ========================================================
    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )
# ============================================================
# START
# ============================================================
if __name__ == "__main__":
    main()