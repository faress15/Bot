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

# راه‌اندازی application به صورت async در Flask context
@app.before_first_request
def init_bot():
    loop = asyncio.get_event_loop()
    loop.create_task(application.initialize())
    loop.create_task(application.start())
    print("✅ Telegram bot application started.")

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
