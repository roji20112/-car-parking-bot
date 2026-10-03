import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")
DB = "bot.db"


def db():
    return sqlite3.connect(DB)


def init_db():
    con = db()
    con.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        username TEXT,
        money INTEGER DEFAULT 50000000,
        coins INTEGER DEFAULT 0,
        cars INTEGER DEFAULT 0,
        premium INTEGER DEFAULT 0,
        access INTEGER DEFAULT 0,
        vinyl TEXT DEFAULT '',
        clones INTEGER DEFAULT 0
    )
    """)
    con.commit()
    con.close()


def add_user(user):
    con = db()

    row = con.execute(
        "SELECT id FROM users WHERE id=?",
        (user.id,)
    ).fetchone()

    if not row:
        con.execute("""
        INSERT INTO users
        (id,name,username)
        VALUES (?,?,?)
        """, (
            user.id,
            user.first_name or "Player",
            user.username or ""
        ))

    con.commit()
    con.close()


def get_user(user_id):
    con = db()
    con.row_factory = sqlite3.Row

    user = con.execute(
        "SELECT * FROM users WHERE id=?",
        (user_id,)
    ).fetchone()

    con.close()
    return user


def keyboard():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "Economy 💰",
                callback_data="economy"
            ),
            InlineKeyboardButton(
                "Account 👤",
                callback_data="account"
            )
        ],

        [
            InlineKeyboardButton(
                "Unlocks 🔓",
                callback_data="unlocks"
            )
        ],

        [
            InlineKeyboardButton(
                "+ Unlock Car 🚘",
                callback_data="car"
            )
        ],

        [
            InlineKeyboardButton(
                "Copy Vinyl 🎨",
                callback_data="vinyl"
            ),
            InlineKeyboardButton(
                "Clone 👥",
                callback_data="clone"
            )
        ],

        [
            InlineKeyboardButton(
                "Access Code 🎟️",
                callback_data="access"
            )
        ],

        [
            InlineKeyboardButton(
                "Subscribe ⭐",
                callback_data="premium"
            )
        ],

        [
            InlineKeyboardButton(
                "Refresh 🔄",
                callback_data="refresh"
            ),
            InlineKeyboardButton(
                "Logout 🚪",
                callback_data="logout"
            )
        ]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    add_user(user)

    data = get_user(user.id)

    text = f"""
👋 <b>Welcome TOOL SIDALI CPM1</b>

👤 Name: {data['name']}
🔹 Username: @{data['username'] or 'None'}
🆔 Telegram ID: <code>{data['id']}</code>

♾ Status: Access granted
⭐ Premium: {'Active' if data['premium'] else 'Not active'}
🎟 Access Code: {'Activated' if data['access'] else 'Not activated'}

👇 Choose a section:
"""

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=keyboard()
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    add_user(query.from_user)

    data = get_user(user_id)

    if query.data == "account":

        text = f"""
👤 <b>Your Information</b>

♾ Status: Access granted
🆔 Telegram ID: <code>{data['id']}</code>

⭐ Premium:
{'Active' if data['premium'] else 'Not active'}

🎟 Access Code:
{'Activated' if data['access'] else 'Not activated'}

━━━━━━━━━━━━━━

👤 Name: {data['name']}
🆔 ID: MF{data['id'] % 1000000:06d}

💵 Money: {data['money']:,}
🪙 Coins: {data['coins']:,}
🚘 Cars owned: {data['cars']}
👥 Clones: {data['clones']}

👇 Choose a section:
"""

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard()
        )


    elif query.data == "economy":

        await query.edit_message_text(
            f"""
💰 <b>ECONOMY</b>

💵 Money: {data['money']:,}
🪙 Coins: {data['coins']:,}

👇 Select:
""",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "💵 +1M",
                        callback_data="money"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🪙 +100 Coins",
                        callback_data="coins"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data="back"
                    )
                ]
            ])
        )


    elif query.data == "money":

        con = db()

        con.execute(
            "UPDATE users SET money=money+1000000 WHERE id=?",
            (user_id,)
        )

        con.commit()
        con.close()

        await query.answer("💵 Money added")

        data = get_user(user_id)

        await query.edit_message_text(
            f"""
💰 <b>ECONOMY</b>

💵 Money: {data['money']:,}
🪙 Coins: {data['coins']:,}
""",
            parse_mode="HTML",
            reply_markup=keyboard()
        )


    elif query.data == "coins":

        con = db()

        con.execute(
            "UPDATE users SET coins=coins+100 WHERE id=?",
            (user_id,)
        )

        con.commit()
        con.close()

        await query.answer("🪙 Coins added")

        data = get_user(user_id)

        await query.edit_message_text(
            f"""
💰 <b>ECONOMY</b>

💵 Money: {data['money']:,}
🪙 Coins: {data['coins']:,}
""",
            parse_mode="HTML",
            reply_markup=keyboard()
        )


    elif query.data == "unlocks":

        await query.edit_message_text(
            """
🔓 <b>UNLOCKS</b>

🚘 Car Unlock
🎨 Vinyl
👥 Clone

Choose an option:
""",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🚘 Unlock Car",
                        callback_data="car"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🎨 Copy Vinyl",
                        callback_data="vinyl"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "👥 Clone",
                        callback_data="clone"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data="back"
                    )
                ]
            ])
        )


    elif query.data == "car":

        con = db()

        con.execute(
            "UPDATE users SET cars=cars+1 WHERE id=?",
            (user_id,)
        )

        con.commit()
        con.close()

        data = get_user(user_id)

        await query.answer("🚘 Car unlocked")

        await query.edit_message_text(
            f"""
🚘 <b>UNLOCK CAR</b>

✅ Car unlocked.

🚘 Cars owned: {data['cars']}
""",
            parse_mode="HTML",
            reply_markup=keyboard()
        )


    elif query.data == "vinyl":

        con = db()

        con.execute(
            "UPDATE users SET vinyl=? WHERE id=?",
            ("DEMO-VINYL", user_id)
        )

        con.commit()
        con.close()

        await query.edit_message_text(
            """
🎨 <b>COPY VINYL</b>

✅ Demo Vinyl generated.

Code:

<code>DEMO-VINYL</code>
""",
            parse_mode="HTML",
            reply_markup=keyboard()
        )


    elif query.data == "clone":

        con = db()

        con.execute(
            "UPDATE users SET clones=clones+1 WHERE id=?",
            (user_id,)
        )

        con.commit()
        con.close()

        data = get_user(user_id)

        await query.edit_message_text(
            f"""
👥 <b>CLONE</b>

✅ Demo clone created.

👥 Clones: {data['clones']}
""",
            parse_mode="HTML",
            reply_markup=keyboard()
        )


    elif query.data == "access":

        con = db()

        con.execute(
            "UPDATE users SET access=1 WHERE id=?",
            (user_id,)
        )

        con.commit()
        con.close()

        await query.answer("🎟 Access activated")

        await query.edit_message_text(
            """
🎟️ <b>ACCESS CODE</b>

✅ Access Code activated.
""",
            parse_mode="HTML",
            reply_markup=keyboard()
        )


    elif query.data == "premium":

        con = db()

        con.execute(
            "UPDATE users SET premium=1 WHERE id=?",
            (user_id,)
        )

        con.commit()
        con.close()

        await query.answer("⭐ Premium activated")

        await query.edit_message_text(
            """
⭐ <b>SUBSCRIBE</b>

✅ Premium activated.
""",
            parse_mode="HTML",
            reply_markup=keyboard()
        )


    elif query.data == "refresh":

        data = get_user(user_id)

        await query.answer("🔄 Refreshed")

        await query.edit_message_text(
            f"""
🔄 <b>REFRESH</b>

💵 Money: {data['money']:,}
🪙 Coins: {data['coins']:,}
🚘 Cars: {data['cars']}
👥 Clones: {data['clones']}
⭐ Premium: {'Active' if data['premium'] else 'Not active'}
""",
            parse_mode="HTML",
            reply_markup=keyboard()
        )


    elif query.data == "logout":

        await query.edit_message_text(
            """
🚪 <b>Logged out</b>

Send /start to open the bot again.
""",
            parse_mode="HTML"
        )


    elif query.data == "back":

        await query.edit_message_text(
            "👇 <b>Choose a section:</b>",
            parse_mode="HTML",
            reply_markup=keyboard()
        )


def main():

    if not TOKEN:
        raise RuntimeError(
            "BOT_TOKEN غير موجود في GitHub Secrets"
        )

    init_db()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CallbackQueryHandler(buttons)
    )

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()