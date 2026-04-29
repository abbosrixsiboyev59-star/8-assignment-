import telebot
import google.generativeai as genai
import os
from flask import Flask

# 1. SOZLAMALAR (Tokenlarni o'zingizniki bilan almashtiring)
BOT_TOKEN = "8763119897:AAGYirxPJtGZni189rq2hT50HuaFnu8oLrY"
AI_API_KEY = "AIzaSyB-GOAHEnU9J889ZSbfPrS-jO95n3UDeKI"

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=AI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Render platformasi uchun kichik veb-server
app = Flask(__name__)
@app.route('/')
def index(): 
    return "Bot ishlamoqda!"

# 2. XABARLARNI QAYTA ISHLASH
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # AI ga foydalanuvchi matnini yuborish
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Hozircha javob bera olmayman, birozdan so'ng urinib ko'ring.")

# 3. ISHGA TUSHIRISH
if __name__ == "__main__":
    import threading
    # Portni Render avtomatik belgilaydi
    port = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port)).start()
    bot.infinity_polling()
