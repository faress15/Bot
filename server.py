from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from bot import start, rank, receive_code
from config import BOT_TOKEN

app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

# افزودن هندلرها
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("rank", rank))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_code))

# نقطه ورود Webhook
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200
