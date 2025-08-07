from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN
from bot import start, rank, receive_code
import asyncio

app = Flask(__name__)

application = Application.builder().token(BOT_TOKEN).build()

# افزودن هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("rank", rank))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_code))

# راه‌اندازی application به صورت async
async def run_bot():
    await application.initialize()
    await application.start()
    print("✅ Telegram bot application started.")

# اجرای ربات هنگام استارت
@app.before_request
def start_bot_once():
    if not hasattr(app, 'bot_started'):
        app.bot_started = True
        asyncio.get_event_loop().create_task(run_bot())

# Webhook endpoint
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200

# صفحه اصلی برای تست
@app.route("/", methods=["GET"])
def home():
    return "Bot is running!", 200
