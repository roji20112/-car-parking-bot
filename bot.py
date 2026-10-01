import os
import asyncio
import tempfile
import subprocess

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

MAX_FILE_SIZE = 1 * 1024 * 1024
TIMEOUT = 20


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🐍 Python Runner Bot\n\n"
        "أرسل لي ملف .py وسأقوم بتشغيله وإرسال النتيجة."
    )


async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):

    document = update.message.document

    if not document.file_name.endswith(".py"):
        await update.message.reply_text(
            "❌ أرسل ملف Python بصيغة .py فقط."
        )
        return

    if document.file_size and document.file_size > MAX_FILE_SIZE:
        await update.message.reply_text(
            "❌ حجم الملف كبير جدًا."
        )
        return

    msg = await update.message.reply_text(
        "⏳ جاري تحميل وتشغيل الملف..."
    )

    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "main.py")

    try:
        file = await document.get_file()
        await file.download_to_drive(file_path)

        process = await asyncio.create_subprocess_exec(
            "docker",
            "run",
            "--rm",
            "--network=none",
            "--memory=128m",
            "--cpus=0.5",
            "--pids-limit=50",
            "-v",
            f"{temp_dir}:/app:ro",
            "python:3.12-alpine",
            "python",
            "/app/main.py",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=TIMEOUT
            )
        except asyncio.TimeoutError:
            process.kill()
            await msg.edit_text(
                "⏱️ تم إيقاف البرنامج لأنه تجاوز الوقت المحدد."
            )
            return

        output = stdout.decode("utf-8", errors="replace")
        error = stderr.decode("utf-8", errors="replace")

        result = output

        if error:
            result += "\n\n❌ ERROR:\n" + error

        if not result.strip():
            result = "✅ انتهى البرنامج بدون إخراج."

        if len(result) > 4000:
            result = result[:4000] + "\n\n... تم اختصار النتيجة."

        await msg.edit_text(
            "📤 النتيجة:\n\n" + result
        )

    except Exception as e:
        await msg.edit_text(
            "❌ حدث خطأ:\n" + str(e)
        )

    finally:
        try:
            os.remove(file_path)
            os.rmdir(temp_dir)
        except:
            pass


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN غير موجود")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.Document.ALL,
            receive_file
        )
    )

    print("🤖 Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()