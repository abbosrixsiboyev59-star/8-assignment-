import telebot
from telebot import types
import sqlite3

TOKEN = "8763119897:AAFlp92HL1GkcQ01QqDOEl1x6ixN8WKk2Eo"   # ⚠️ вставь новый токен
ADMIN_ID = 6075254042

bot = telebot.TeleBot(TOKEN)

# ================== DATABASE ==================
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT
)
""")
conn.commit()


def add_user(user):
    cursor.execute("SELECT id FROM users WHERE id=?", (user.id,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (id, username, first_name) VALUES (?, ?, ?)",
            (user.id, user.username, user.first_name)
        )
        conn.commit()


# ================== STATE ==================
reply_user = {}  # admin_id -> user_id


# ================== CALLBACK ==================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    data = call.data.split(":")
    action = data[0]
    user_id = int(data[1])

    if action == "reply":
        reply_user[call.from_user.id] = user_id
        bot.send_message(call.from_user.id, "✍️ Напиши ответ пользователю")

    elif action == "ignore":
        bot.send_message(user_id, ai_reply())
        bot.answer_callback_query(call.id, "Авто-ответ отправлен")


# ================== ADMIN REPLY ==================
@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID)
def admin_reply(message):

    # проверяем есть ли ожидаемый пользователь
    if message.chat.id not in reply_user:
        return

    user_id = reply_user[message.chat.id]

    try:
        if message.text:
            bot.send_message(user_id, message.text)

        elif message.photo:
            bot.send_photo(user_id, message.photo[-1].file_id)

        elif message.voice:
            bot.send_voice(user_id, message.voice.file_id)

        elif message.video:
            bot.send_video(user_id, message.video.file_id)

        elif message.sticker:
            bot.send_sticker(user_id, message.sticker.file_id)

        elif message.animation:
            bot.send_animation(user_id, message.animation.file_id)

        bot.send_message(ADMIN_ID, "✅ Отправлено")

    except:
        bot.send_message(ADMIN_ID, "❌ Ошибка отправки")

    # очищаем состояние
    reply_user.pop(message.chat.id, None)

# ================== START ==================
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    add_user(user)

    bot.send_message(
        message.chat.id,
        "👋 Отправь любое сообщение, фото, видео и т.д."
    )

    if message.chat.id != ADMIN_ID:
        bot.send_message(
            ADMIN_ID,
            f"🚀 Новый пользователь:\n{user.first_name}\nID: {user.id}"
        )


# ================== HANDLE ALL ==================
@bot.message_handler(content_types=[
    'text', 'photo', 'voice', 'video', 'video_note', 'sticker', 'animation'
])
def handle_all(message):
    user = message.from_user
    add_user(user)

    if message.chat.id == ADMIN_ID:
        return

    text = f"📩 {user.first_name} | ID: {user.id}"

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Ответить", callback_data=f"reply:{user.id}"),
        types.InlineKeyboardButton("❌ Игнор", callback_data=f"ignore:{user.id}")
    )

    if message.text:
        bot.send_message(ADMIN_ID, f"💬 {text}\n\n{message.text}", reply_markup=markup)

    elif message.photo:
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=text, reply_markup=markup)

    elif message.voice:
        bot.send_voice(ADMIN_ID, message.voice.file_id)
        bot.send_message(ADMIN_ID, text, reply_markup=markup)

    elif message.video:
        bot.send_video(ADMIN_ID, message.video.file_id, caption=text, reply_markup=markup)

    elif message.video_note:
        bot.send_video_note(ADMIN_ID, message.video_note.file_id)
        bot.send_message(ADMIN_ID, text, reply_markup=markup)

    elif message.sticker:
        bot.send_sticker(ADMIN_ID, message.sticker.file_id)
        bot.send_message(ADMIN_ID, text, reply_markup=markup)

    elif message.animation:
        bot.send_animation(ADMIN_ID, message.animation.file_id)
        bot.send_message(ADMIN_ID, text, reply_markup=markup)


# ================== CALLBACK ==================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    data = call.data.split(":")
    action = data[0]
    user_id = int(data[1])

    if action == "reply":
        reply_user["active"] = user_id
        bot.send_message(ADMIN_ID, "✍️ Напиши ответ пользователю")

    elif action == "ignore":
        bot.send_message(user_id, ai_reply())
        bot.answer_callback_query(call.id, "Авто-ответ отправлен")


# ================== ADMIN REPLY ==================
@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID)
def admin_reply(message):

    user_id = reply_user.get("active")

    if not user_id:
        return

    try:
        if message.text:
            bot.send_message(user_id, message.text)

        elif message.photo:
            bot.send_photo(user_id, message.photo[-1].file_id)

        elif message.voice:
            bot.send_voice(user_id, message.voice.file_id)

        elif message.video:
            bot.send_video(user_id, message.video.file_id)

        elif message.sticker:
            bot.send_sticker(user_id, message.sticker.file_id)

        elif message.animation:
            bot.send_animation(user_id, message.animation.file_id)

        bot.send_message(ADMIN_ID, "✅ Отправлено")

    except:
        bot.send_message(ADMIN_ID, "❌ Ошибка отправки")

    reply_user.pop("active", None)


# ================== ADMIN PANEL ==================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("👥 Пользователи", "📢 Рассылка")

    bot.send_message(message.chat.id, "⚙️ Админ панель", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "👥 Пользователи")
def users(message):
    if message.chat.id != ADMIN_ID:
        return

    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()

    bot.send_message(message.chat.id, f"👥 Пользователей: {len(data)}")


@bot.message_handler(func=lambda m: m.text == "📢 Рассылка")
def broadcast(message):
    if message.chat.id != ADMIN_ID:
        return

    msg = bot.send_message(message.chat.id, "✍️ Введи текст рассылки:")
    bot.register_next_step_handler(msg, send_broadcast)


def send_broadcast(message):
    cursor.execute("SELECT id FROM users")
    users = cursor.fetchall()

    count = 0

    for u in users:
        try:
            bot.send_message(u[0], message.text)
            count += 1
        except:
            pass

    bot.send_message(message.chat.id, f"✅ Отправлено: {count}")


# ================== RUN ==================
print("Bot ishlayapti...")
bot.infinity_polling()
