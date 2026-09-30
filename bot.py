import os
import json
import telebot
from telebot import types

# ==============================
# SETTINGS
# ==============================

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8514140307
SERVICES_FILE = "services.json"

if not TOKEN:
    raise ValueError("BOT_TOKEN is missing")

bot = telebot.TeleBot(TOKEN)

# حالات الأدمن
admin_state = {}


# ==============================
# DATABASE
# ==============================

def load_services():
    try:
        with open(SERVICES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_services(services):
    with open(SERVICES_FILE, "w", encoding="utf-8") as f:
        json.dump(
            services,
            f,
            ensure_ascii=False,
            indent=2
        )


def is_admin(user_id):
    return user_id == ADMIN_ID


# ==============================
# MAIN MENU
# ==============================

def main_menu(user_id):

    keyboard = types.InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        types.InlineKeyboardButton(
            "🚗 الخدمات",
            callback_data="services"
        ),
        types.InlineKeyboardButton(
            "📞 الدعم",
            callback_data="support"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "ℹ️ معلومات",
            callback_data="info"
        )
    )

    if is_admin(user_id):
        keyboard.add(
            types.InlineKeyboardButton(
                "🔐 لوحة الإدارة",
                callback_data="admin"
            )
        )

    return keyboard


# ==============================
# START
# ==============================

@bot.message_handler(commands=["start"])
def start(message):

    bot.send_message(
        message.chat.id,
        "🚗 <b>Car Parking Bot</b>\n\n"
        "مرحبا بك 👋\n"
        "اختار واش حاب من القائمة 👇",
        parse_mode="HTML",
        reply_markup=main_menu(message.from_user.id)
    )


# ==============================
# SERVICES MENU
# ==============================

def services_menu():

    keyboard = types.InlineKeyboardMarkup()

    services = load_services()

    if services:

        for i, service in enumerate(services):

            keyboard.add(
                types.InlineKeyboardButton(
                    f"🚗 {service['name']}",
                    callback_data=f"service:{i}"
                )
            )

    keyboard.add(
        types.InlineKeyboardButton(
            "🔙 رجوع",
            callback_data="home"
        )
    )

    return keyboard


# ==============================
# ADMIN MENU
# ==============================

def admin_menu():

    keyboard = types.InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        types.InlineKeyboardButton(
            "➕ إضافة خدمة",
            callback_data="add"
        ),
        types.InlineKeyboardButton(
            "✏️ تعديل خدمة",
            callback_data="edit"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🗑️ حذف خدمة",
            callback_data="delete"
        ),
        types.InlineKeyboardButton(
            "📋 الخدمات",
            callback_data="admin_services"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🔙 القائمة الرئيسية",
            callback_data="home"
        )
    )

    return keyboard


# ==============================
# CALLBACKS
# ==============================

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    data = call.data

    bot.answer_callback_query(call.id)

    # --------------------------
    # HOME
    # --------------------------

    if data == "home":

        bot.edit_message_text(
            "🚗 <b>Car Parking Bot</b>\n\n"
            "اختار الخدمة 👇",
            chat_id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=main_menu(user_id)
        )

    # --------------------------
    # SERVICES
    # --------------------------

    elif data == "services":

        services = load_services()

        if not services:

            text = (
                "🚗 <b>الخدمات</b>\n\n"
                "❌ حاليا ما كاين حتى خدمة."
            )

        else:

            text = (
                "🚗 <b>الخدمات المتوفرة</b>\n\n"
                "اختار الخدمة 👇"
            )

        bot.edit_message_text(
            text,
            chat_id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=services_menu()
        )

    # --------------------------
    # SERVICE DETAILS
    # --------------------------

    elif data.startswith("service:"):

        try:
            index = int(data.split(":")[1])
        except:
            return

        services = load_services()

        if index >= len(services):
            return

        service = services[index]

        text = (
            f"🚗 <b>{service['name']}</b>\n\n"
            f"💰 السعر: <b>{service['price']}</b>\n\n"
            f"📝 {service['description']}"
        )

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "🔙 الخدمات",
                callback_data="services"
            )
        )

        bot.edit_message_text(
            text,
            chat_id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    # --------------------------
    # SUPPORT
    # --------------------------

    elif data == "support":

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "🔙 رجوع",
                callback_data="home"
            )
        )

        bot.edit_message_text(
            "📞 <b>الدعم</b>\n\n"
            "للتواصل مع الإدارة أرسل رسالة مباشرة.",
            chat_id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    # --------------------------
    # INFO
    # --------------------------

    elif data == "info":

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "🔙 رجوع",
                callback_data="home"
            )
        )

        bot.edit_message_text(
            "ℹ️ <b>Car Parking Bot</b>\n\n"
            "🚗 بوت لخدمات Car Parking.",
            chat_id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    # ==========================
    # ADMIN
    # ==========================

    elif data == "admin":

        if not is_admin(user_id):
            return

        bot.edit_message_text(
            "🔐 <b>لوحة الإدارة</b>\n\n"
            "اختار العملية 👇",
            chat_id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=admin_menu()
        )

    # --------------------------
    # ADD
    # --------------------------

    elif data == "add":

        if not is_admin(user_id):
            return

        admin_state[user_id] = {
            "action": "add",
            "step": "name"
        }

        bot.send_message(
            chat_id,
            "➕ <b>إضافة خدمة</b>\n\n"
            "أرسل اسم الخدمة:",
            parse_mode="HTML"
        )

    # --------------------------
    # DELETE MENU
    # --------------------------

    elif data == "delete":

        if not is_admin(user_id):
            return

        services = load_services()

        keyboard = types.InlineKeyboardMarkup()

        if not services:

            bot.send_message(
                chat_id,
                "❌ ما كاين حتى خدمة للحذف."
            )
            return

        for i, service in enumerate(services):

            keyboard.add(
                types.InlineKeyboardButton(
                    f"🗑️ {service['name']}",
                    callback_data=f"delete:{i}"
                )
            )

        keyboard.add(
            types.InlineKeyboardButton(
                "🔙 رجوع",
                callback_data="admin"
            )
        )

        bot.send_message(
            chat_id,
            "🗑️ <b>اختار الخدمة للحذف:</b>",
            parse_mode="HTML",
            reply_markup=keyboard
        )

    # --------------------------
    # DELETE
    # --------------------------

    elif data.startswith("delete:"):

        if not is_admin(user_id):
            return

        try:
            index = int(data.split(":")[1])
        except:
            return

        services = load_services()

        if index >= len(services):
            return

        name = services[index]["name"]

        services.pop(index)

        save_services(services)

        bot.send_message(
            chat_id,
            f"✅ تم حذف الخدمة:\n🚗 {name}"
        )

    # --------------------------
    # ADMIN SERVICES
    # --------------------------

    elif data == "admin_services":

        if not is_admin(user_id):
            return

        services = load_services()

        if not services:

            text = "📋 ما كاين حتى خدمة."
        else:

            text = "📋 <b>الخدمات الحالية:</b>\n\n"

            for i, service in enumerate(services, 1):

                text += (
                    f"{i}. 🚗 <b>{service['name']}</b>\n"
                    f"💰 {service['price']}\n"
                    f"📝 {service['description']}\n\n"
                )

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "🔙 رجوع",
                callback_data="admin"
            )
        )

        bot.send_message(
            chat_id,
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    # --------------------------
    # EDIT MENU
    # --------------------------

    elif data == "edit":

        if not is_admin(user_id):
            return

        services = load_services()

        if not services:

            bot.send_message(
                chat_id,
                "❌ ما كاين حتى خدمة للتعديل."
            )
            return

        keyboard = types.InlineKeyboardMarkup()

        for i, service in enumerate(services):

            keyboard.add(
                types.InlineKeyboardButton(
                    f"✏️ {service['name']}",
                    callback_data=f"edit:{i}"
                )
            )

        keyboard.add(
            types.InlineKeyboardButton(
                "🔙 رجوع",
                callback_data="admin"
            )
        )

        bot.send_message(
            chat_id,
            "✏️ <b>اختار الخدمة للتعديل:</b>",
            parse_mode="HTML",
            reply_markup=keyboard
        )

    # --------------------------
    # EDIT SERVICE
    # --------------------------

    elif data.startswith("edit:"):

        if not is_admin(user_id):
            return

        try:
            index = int(data.split(":")[1])
        except:
            return

        services = load_services()

        if index >= len(services):
            return

        admin_state[user_id] = {
            "action": "edit",
            "step": "name",
            "index": index
        }

        bot.send_message(
            chat_id,
            "✏️ أرسل الاسم الجديد للخدمة:"
        )


# ==============================
# ADMIN TEXT
# ==============================

@bot.message_handler(
    func=lambda message: message.from_user.id == ADMIN_ID
)
def admin_text(message):

    user_id = message.from_user.id

    if user_id not in admin_state:
        return

    state = admin_state[user_id]

    # --------------------------
    # NAME
    # --------------------------

    if state["step"] == "name":

        state["name"] = message.text
        state["step"] = "price"

        bot.send_message(
            message.chat.id,
            "💰 أرسل السعر:"
        )

    # --------------------------
    # PRICE
    # --------------------------

    elif state["step"] == "price":

        state["price"] = message.text
        state["step"] = "description"

        bot.send_message(
            message.chat.id,
            "📝 أرسل وصف الخدمة:"
        )

    # --------------------------
    # DESCRIPTION
    # --------------------------

    elif state["step"] == "description":

        state["description"] = message.text

        services = load_services()

        # إضافة
        if state["action"] == "add":

            services.append({
                "name": state["name"],
                "price": state["price"],
                "description": state["description"]
            })

            save_services(services)

            bot.send_message(
                message.chat.id,
                "✅ <b>تمت إضافة الخدمة بنجاح!</b> 🚗",
                parse_mode="HTML",
                reply_markup=admin_menu()
            )

        # تعديل
        elif state["action"] == "edit":

            index = state["index"]

            if index < len(services):

                services[index] = {
                    "name": state["name"],
                    "price": state["price"],
                    "description": state["description"]
                }

                save_services(services)

                bot.send_message(
                    message.chat.id,
                    "✅ <b>تم تعديل الخدمة بنجاح!</b> ✏️",
                    parse_mode="HTML",
                    reply_markup=admin_menu()
                )

        del admin_state[user_id]


# ==============================
# USER ID
# ==============================

@bot.message_handler(commands=["id"])
def get_id(message):

    bot.send_message(
        message.chat.id,
        f"🆔 ID تاعك:\n\n<code>{message.from_user.id}</code>",
        parse_mode="HTML"
    )


# ==============================
# RUN
# ==============================

print("🚗 Car Parking Bot Started!")

bot.infinity_polling(
    skip_pending=True
)