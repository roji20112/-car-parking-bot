import os
import json
import telebot
from telebot import types

# =========================
# إعدادات البوت
# =========================

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8514140307

bot = telebot.TeleBot(TOKEN)

SERVICES_FILE = "services.json"

# =========================
# الخدمات
# =========================

def load_services():
    if not os.path.exists(SERVICES_FILE):
        return []

    try:
        with open(SERVICES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return []


def save_services(services):
    with open(SERVICES_FILE, "w", encoding="utf-8") as file:
        json.dump(
            services,
            file,
            ensure_ascii=False,
            indent=2
        )


# حالات إضافة الخدمة
admin_state = {}


def is_admin(user_id):
    return user_id == ADMIN_ID


# =========================
# /start
# =========================

@bot.message_handler(commands=["start"])
def start(message):

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

    # زر الإدارة يظهر لك أنت فقط
    if is_admin(message.from_user.id):
        keyboard.add(
            types.InlineKeyboardButton(
                "🔐 لوحة الإدارة",
                callback_data="admin"
            )
        )

    bot.send_message(
        message.chat.id,
        "🚗 أهلا وسهلا بك في Car Parking Bot\n\n"
        "اختار الخدمة من الأسفل 👇",
        reply_markup=keyboard
    )


# =========================
# عرض الخدمات
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "services"
)
def services_button(call):

    bot.answer_callback_query(call.id)

    services = load_services()

    if not services:
        bot.send_message(
            call.message.chat.id,
            "🚗 ما كاين حتى خدمة حاليا."
        )
        return

    keyboard = types.InlineKeyboardMarkup()

    for i, service in enumerate(services):

        keyboard.add(
            types.InlineKeyboardButton(
                f"🚗 {service['name']}",
                callback_data=f"view_{i}"
            )
        )

    bot.send_message(
        call.message.chat.id,
        "🚗 اختار الخدمة:",
        reply_markup=keyboard
    )


# =========================
# مشاهدة الخدمة
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("view_")
)
def view_service(call):

    bot.answer_callback_query(call.id)

    try:
        index = int(call.data.split("_")[1])
    except:
        return

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


# =========================
# الدعم
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "support"
)
def support(call):

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        "📞 للدعم تواصل مع الإدارة.@M31_ROJI2"
    )


# =========================
# معلومات
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "info"
)
def info(call):

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        "ℹ️ Car Parking Bot\n\n"
        "🚗 خدمات Car Parking"
    )


# =========================
# لوحة الإدارة
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "admin"
)
def admin_button(call):

    bot.answer_callback_query(call.id)

    if not is_admin(call.from_user.id):

        bot.send_message(
            call.message.chat.id,
            "⛔ ما عندكش صلاحية."
        )
        return

    admin_panel(call.message.chat.id)


def admin_panel(chat_id):

    keyboard = types.InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        types.InlineKeyboardButton(
            "➕ إضافة خدمة",
            callback_data="add_service"
        ),
        types.InlineKeyboardButton(
            "🗑️ حذف خدمة",
            callback_data="delete_service"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "📋 عرض الخدمات",
            callback_data="admin_list"
        )
    )

    bot.send_message(
        chat_id,
        "🔐 لوحة الإدارة 👑\n\n"
        "اختار العملية:",
        reply_markup=keyboard
    )


# =========================
# إضافة خدمة
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "add_service"
)
def add_service(call):

    bot.answer_callback_query(call.id)

    if not is_admin(call.from_user.id):
        return

    admin_state[call.from_user.id] = {
        "step": "name"
    }

    bot.send_message(
        call.message.chat.id,
        "➕ إضافة خدمة\n\n"
        "1️⃣ اكتب اسم الخدمة:"
    )


# =========================
# حذف خدمة
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "delete_service"
)
def delete_service(call):

    bot.answer_callback_query(call.id)

    if not is_admin(call.from_user.id):
        return

    services = load_services()

    if not services:

        bot.send_message(
            call.message.chat.id,
            "❌ ما كاين حتى خدمة."
        )
        return

    keyboard = types.InlineKeyboardMarkup()

    for i, service in enumerate(services):

        keyboard.add(
            types.InlineKeyboardButton(
                f"🗑️ {service['name']}",
                callback_data=f"del_{i}"
            )
        )

    bot.send_message(
        call.message.chat.id,
        "🗑️ اختار الخدمة لي تحب تحذفها:",
        reply_markup=keyboard
    )


# =========================
# حذف فعلي
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("del_")
)
def delete_confirm(call):

    bot.answer_callback_query(call.id)

    if not is_admin(call.from_user.id):
        return

    try:
        index = int(call.data.split("_")[1])
    except:
        return

    services = load_services()

    if index >= len(services):
        return

    deleted = services.pop(index)

    save_services(services)

    bot.send_message(
        call.message.chat.id,
        f"✅ تم حذف:\n🚗 {deleted['name']}"
    )


# =========================
# عرض الخدمات للأدمن
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data == "admin_list"
)
def admin_list(call):

    bot.answer_callback_query(call.id)

    if not is_admin(call.from_user.id):
        return

    services = load_services()

    if not services:

        bot.send_message(
            call.message.chat.id,
            "📋 ما كاين حتى خدمة."
        )
        return

    text = "📋 الخدمات الحالية:\n\n"

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
# إدخال معلومات الخدمة
# =========================

@bot.message_handler(
    func=lambda message: message.from_user.id == ADMIN_ID
)
def admin_text(message):

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
            "2️⃣ اكتب سعر الخدمة:"
        )

    # السعر
    elif state["step"] == "price":

        state["price"] = message.text
        state["step"] = "description"

        bot.send_message(
            message.chat.id,
            "3️⃣ اكتب وصف الخدمة:"
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
            "✅ تمت إضافة الخدمة بنجاح 🚗🔥"
        )

        admin_panel(message.chat.id)


# =========================
# معرفة ID
# =========================

@bot.message_handler(commands=["id"])
def get_id(message):

    bot.send_message(
        message.chat.id,
        f"🆔 ID تاعك:\n\n{message.from_user.id}"
    )


# =========================
# تشغيل البوت
# =========================

print("🚗 Car Parking Bot is running...")

bot.infinity_polling()