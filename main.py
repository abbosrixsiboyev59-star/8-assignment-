@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        # Xatolikni rasmda ko'rsatilgan matn o'rniga aynan nima ekanligini yuboradi
        bot.reply_to(message, f"Xato yuz berdi: {str(e)}")
