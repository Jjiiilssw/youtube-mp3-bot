import os
import asyncio
import tempfile

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import yt_dlp


BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋\n\n"
        "Отправь мне ссылку на YouTube, и я попробую получить аудио."
    )


async def download_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text(
            "Пожалуйста, отправь ссылку на YouTube."
        )
        return

    message = await update.message.reply_text(
        "⏳ Загружаю аудио..."
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        output = os.path.join(temp_dir, "%(title)s.%(ext)s")

        options = {
            "format": "bestaudio/best",
            "outtmpl": output,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            await message.edit_text("📤 Отправляю файл...")

            with open(filename, "rb") as audio:
                await update.message.reply_audio(
                    audio=audio,
                    title=info.get("title", "audio"),
                )

            await message.delete()

        except Exception as e:
            print(e)

            await message.edit_text(
                "❌ Не удалось обработать эту ссылку."
            )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не установлен")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            download_audio,
        )
    )

    print("Бот запущен!")

    app.run_polling()


if __name__ == "__main__":
    main()
