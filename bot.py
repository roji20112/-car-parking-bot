import os
import json
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8514140307

bot = telebot.TeleBot(TOKEN)

FILE = "users.json"

user_state = {}


# =====================
# DATABASE
# =====================

def load_users():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_users(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =====================
# MENU
# =====================

def menu(user_id):

    kb = types.InlineKeyboardMarkup(row_width=2)

    kb.add(
        types.InlineKeyboardButton(
            "👤 حسابي",
            callback_data="account"
        ),
        types.InlineKeyboardButton(
            "🚗 إضافة حساب",
            callback_data="add_account"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "💰 المال",
            callback_data="money"
        ),
        types.InlineKeyboardButton(
            "🪙 Coins",
            callback_data="coins"
        )
    )

    if user_id == ADMIN_ID:
        kb.add(
            types.InlineKeyboardButton(
                "👑 Admin",
                callback_data="admin"
            )
        )

    return kb


# =====================
# START
# =====================

@bot.message_handler(commands=["start"])
def start(message):

    bot.send_message(
        message.chat.id,
        "🚗 Car Parking Bot\n\nاختر:",
        reply_markup=menu(message.from_user.id)
    )


# =====================
# BUTTONS
# =====================

@bot.callback_query_handler(func=lambda c: True)
def buttons(call):

    uid = str(call.from_user.id)
    users = load_users()

    if call.data == "account":

        if uid not in users:

            bot.send_message(
                call.message.chat.id,
                "❌ لا يوجد حساب"
            )

        else:

            u = users[uid]

            bot.send_message(
                call.message.chat.id,
                f"👤 حسابك\n\n"
                f"🚗 ID: {u['car_id']}\n"
                f"💰 المال: {u['money']}\n"
                f"🪙 Coins: {u['coins']}"
            )


    elif call.data == "add_account":

        user_state[uid] = "car_id"

        bot.send_message(
            call.message.chat.id,
            "🚗 أرسل ID حساب Car Parking:"
        )


    elif call.data == "money":

        money = users.get(uid, {}).get("money",0)

        bot.send_message(
            call.message.chat.id,
            f"💰 المال: {money}"
        )


    elif call.data == "coins":

        coins = users.get(uid, {}).get("coins",0)

        bot.send_message(
            call.message.chat.id,
            f"🪙 Coins: {coins}"
        )


    elif call.data == "admin":

        if call.from_user.id != ADMIN_ID:
            return

        bot.send_message(
            call.message.chat.id,
            "👑 لوحة Admin\n\n"
            "عدد المستخدمين: "
            + str(len(users))
        )


# =====================
# USER INPUT
# =====================

@bot.message_handler(func=lambda m: True)
def text(message):

    uid = str(message.from_user.id)

    if uid not in user_state:
        return


    if user_state[uid] == "car_id":

        users = load_users()

        users[uid] = {
            "car_id": message.text,
            "money": 0,
            "coins": 0
        }

        save_users(users)

        del user_state[uid]


        bot.send_message(
            message.chat.id,
            "✅ تم إضافة حساب Car Parking",
            reply_markup=menu(message.from_user.id)
        )


# =====================
# RUN
# =====================

print("BOT STARTED")

bot.infinity_polling()