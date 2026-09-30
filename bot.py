import os
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    btn1 = types.InlineKeyboardButton("🚗 Car Parking", callback_data="carparking")
    btn2 = types.InlineKeyboardButton("🛠️ الخدمات", callback_data="services")
    btn3 = types.InlineKeyboardButton("📞 الدعم", callback_data="support")
    btn4 = types.InlineKeyboardButton("ℹ️ معلومات", callback_data="info")

    keyboard.add(btn1, btn2)
    keyboard.add(btn3, btn4)

    bot.send_message(
        message.chat.id,
        "🚗 مرحبا بك في Car Parking Bot!\n\n"
        "اختار الخدمة من الأزرار 👇",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: True)
def buttons(call):

    if call.data == "carparking":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "🚗 خدمات Car Parking\n\n"
            "🔧 الخدمة غير متاحة حاليا.\n"
            "سيتم إضافة الخدمات قريبا."
        )

    elif call.data == "services":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "🛠️ الخدمات:\n\n"
            "🚗 Car Parking\n"
            "📦 خدمات أخرى قريبا..."
        )

    elif call.data == "support":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "📞 للدعم تواصل مع الإدارة."
        )

    elif call.data == "info":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "ℹ️ Car Parking Bot\n"
            "بوت لخدمات Car Parking 🚗"
        )

print("Bot is running...")
bot.infinity_polling()