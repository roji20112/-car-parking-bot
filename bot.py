import os
import telebot
from telebot import import os
import json
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8514140307

bot = telebot.TeleBot(TOKEN)

SERVICES_FILE = "services.json"

# =========================
# SERVICES
# =========================

def load_services():
    if not os.path.exists(SERVICES_FILE):
        return []

    try:
        with open(SERVICES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_services(services):
    with open(SERVICES_FILE, "w", encoding="utf-8") as f:
        json.dump(services, f, ensure_ascii=False, indent=2)


services = load_services()

# تخزين حالة الأدمن
admin_state = {}


def is_admin(user_id):
    return user_id == ADMIN_ID


# =========================
# START
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    keyboard = types.InlineKeyboardMarkup(row_width=2)

    btn1 = types.InlineKeyboardButton(
        "🚗 الخدمات",
        callback_data="services"
    )

    btn2 = types.InlineKeyboardButton(
        "📞 الدعم",
        callback_data="support"
    )

    btn3 = types.InlineKeyboardButton(
        "ℹ️ معلومات",
        callback_data="info"
    )

    keyboard.add(btn1, btn2)
    keyboard.add(btn3)

    if is_admin(message.from_user.id):
        admin_btn = types.InlineKeyboardButton(
            "🔐 لوحة الإدارة",
            callback_data="admin"
        )
        keyboard.add(admin_btn)

    bot.send_message(
        message.chat.id,
        "🚗 أهلا وسهلا بك في Car Parking Bot\n\n"
        "اختار الخدمة من القائمة 👇",
        reply_markup=keyboard
    )


# =========================
# SERVICES
# =========================

def show_services(chat_id):

    services = load_services()

    keyboard = types.InlineKeyboardMarkup()

    if not services:
        bot.send_message(
            chat_id,
            "🚗 حاليا ما كاين حتى خدمة مضافة."
        )
        return

    for i, service in enumerate(services):
        keyboard.add(
            types.InlineKeyboardButton(
                f"🚗 {service['name']}",
                callback_data=f"view_{i}"
            )
        )

    bot.send_message(
        chat_id,
        "🚗 خدماتنا:\n\n"
        "اختار الخدمة لي حاب تشوفها 👇",
        reply_markup=keyboard
    )


# =========================
# BUTTONS
# =========================

@bot.callback_query_handler(func=lambda call: True)
def buttons(call):

    user_id = call.from_user.id

    # الخدمات
    if call.data == "services":

        bot.answer_callback_query(call.id)

        show_services(call.message.chat.id)

    # عرض خدمة
    elif call.data.startswith("view_"):

        bot.answer_callback_query(call.id)

        index = int(call.data.split("_")[1])

        services = load_services()

        if index >= len(services):
            return

        service = services[index]

        text = (
            f"🚗 {service['name']}\n\n"
            f"💰 السعر: {service['price']}\n\n"
            f"📝 {service['description']}"
        )

        bot.send_message(
            call.message.chat.id,
            text
        )

    # الدعم
    elif call.data == "support":

        bot.answer_callback_query(call.id)

        bot.send_message(
            call.message.chat.id,
            "📞 للدعم تواصل مع الإدارة."
        )

    # معلومات
    elif call.data == "info":

        bot.answer_callback_query(call.id)

        bot.send_message(
            call.message.chat.id,
            "ℹ️ Car Parking Bot\n\n"
            "🚗 بوت خاص بخدمات Car Parking."
        )

    # لوحة الإدارة
    elif call.data == "admin":

        bot.answer_callback_query(call.id)

        if not is_admin(user_id):
            bot.send_message(
                call.message.chat.id,
                "⛔ ما عندكش صلاحية."
            )
            return

        admin_panel(call.message.chat.id)

    # إضافة خدمة
    elif call.data == "add_service":

        bot.answer_callback_query(call.id)

        if not is_admin(user_id):
            return

        admin_state[user_id] = {
            "action": "add",
            "step": "name"
        }

        bot.send_message(
            call.message.chat.id,
            "➕ إضافة خدمة\n\n"
            "اكتب اسم الخدمة:"
        )

    # حذف خدمة
    elif call.data == "delete_service":

        bot.answer_callback_query(call.id)

        if not is_admin(user_id):
            return

        services = load_services()

        if not services:
            bot.send_message(
                call.message.chat.id,
                "❌ ما كاين حتى خدمة للحذف."
            )
            return

        keyboard = types.InlineKeyboardMarkup()

        for i, service in enumerate(services):
            keyboard.add(
                types.InlineKeyboardButton(
                    f"🗑️ {service['name']}",
                    callback_data=f"delete_{i}"
                )
            )

        bot.send_message(
            call.message.chat.id,
            "🗑️ اختار الخدمة لي تحب تحذفها:",
            reply_markup=keyboard
        )

    # حذف فعلي
    elif call.data.startswith("delete_"):

        bot.answer_callback_query(call.id)

        if not is_admin(user_id):
            return

        index = int(call.data.split("_")[1])

        services = load_services()

        if index >= len(services):
            return

        deleted = services.pop(index)

        save_services(services)

        bot.send_message(
            call.message.chat.id,
            f"✅ تم حذف الخدمة:\n{deleted['name']}"
        )

    # عرض الخدمات للأدمن
    elif call.data == "admin_services":

        bot.answer_callback_query(call.id)

        if not is_admin(user_id):
            return

        services = load_services()

        if not services:
            bot.send_message(
                call.message.chat.id,
                "📋 ما كاين حتى خدمة."
            )
            return

        text = "📋 الخدمات الموجودة:\n\n"

        for i, service in enumerate(services, 1):
            text += (
                f"{i}. 🚗 {service['name']}\n"
                f"💰 {service['price']}\n"
                f"📝 {service['description']}\n\n"
            )

        bot.send_message(
            call.message.chat.id,
            text
        )


# =========================
# ADMIN PANEL
# =========================

def admin_panel(chat_id):

    keyboard = types.InlineKeyboardMarkup(row_width=2)

    add = types.InlineKeyboardButton(
        "➕ إضافة خدمة",
        callback_data="add_service"
    )

    delete = types.InlineKeyboardButton(
        "🗑️ حذف خدمة",
        callback_data="delete_service"
    )

    list_services = types.InlineKeyboardButton(
        "📋 الخدمات",
        callback_data="admin_services"
    )

    keyboard.add(add, delete)
    keyboard.add(list_services)

    bot.send_message(
        chat_id,
        "🔐 لوحة الإدارة\n\n"
        "مرحبا Admin 👑\n"
        "اختار العملية:",
        reply_markup=keyboard
    )


# =========================
# ADMIN TEXT INPUT
# =========================

@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID)
def admin_messages(message):

    user_id = message.from_user.id

    if user_id not in admin_state:
        return

    state = admin_state[user_id]

    # اسم الخدمة
    if state["step"] == "name":

        state["name"] = message.text
        state["step"] = "price"

        bot.send_message(
            message.chat.id,
            "💰 اكتب سعر الخدمة:"
        )

    # السعر
    elif state["step"] == "price":

        state["price"] = message.text
        state["step"] = "description"

        bot.send_message(
            message.chat.id,
            "📝 اكتب وصف الخدمة:"
        )

    # الوصف
    elif state["step"] == "description":

        state["description"] = message.text

        services = load_services()

        services.append({
            "name": state["name"],
            "price": state["price"],
            "description": state["description"]
        })

        save_services(services)

        del admin_state[user_id]

        bot.send_message(
            message.chat.id,
            "✅ تمت إضافة الخدمة بنجاح! 🚗"
        )

        admin_panel(message.chat.id)


# =========================
# SHOW USER ID
# =========================

@bot.message_handler(commands=["id"])
def get_id(message):

    bot.send_message(
        message.chat.id,
        f"🆔 User ID تاعك هو:\n\n{message.from_user.id}"
    )


# =========================
# START BOT
# =========================

print("🚗 Car Parking Bot is running...")

bot.infinity_polling()

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