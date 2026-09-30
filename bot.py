import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "🚗 مرحبا بك في Car Parking Bot!\n\n"
        "اختار الخدمة:\n"
        "🎮 Car Parking\n"
        "🛠️ الخدمات\n"
        "📞 الدعم"
    )

@bot.message_handler(commands=["help"])
def help_command(message):
    bot.reply_to(
        message,
        "📋 الأوامر:\n"
        "/start - تشغيل البوت\n"
        "/help - المساعدة"
    )

@bot.message_handler(func=lambda message: True)
def messages(message):
    bot.reply_to(
        message,
        "✅ وصلت رسالتك!\n"
        "استعمل /start لرؤية الخدمات."
    )

print("Bot is running...")
bot.infinity_polling()
