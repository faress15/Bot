# from flask import Flask, request
# from telegram import Update
# from telegram.ext import Application, CommandHandler, MessageHandler, filters
# from config import BOT_TOKEN
# from bot import start, rank, receive_code
# import asyncio
# import threading

# app = Flask(__name__)
# application = Application.builder().token(BOT_TOKEN).build()

# # هندلرها
# application.add_handler(CommandHandler("start", start))
# application.add_handler(CommandHandler("rank", rank))
# application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_code))

# async def start_bot():
#     await application.initialize()
#     await application.start()
#     print("✅ Telegram bot started")

# # اجرای async loop در یک ترد جداگانه (Background Thread)
# def run_async_bot():
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(start_bot())
#     loop.run_forever()

# # هنگام لود شدن ماژول، ترد راه‌اندازی بات رو اجرا کن
# threading.Thread(target=run_async_bot, daemon=True).start()

# @app.route(f"/{BOT_TOKEN}", methods=["POST"])
# def webhook():
#     update = Update.de_json(request.get_json(force=True), application.bot)
#     application.update_queue.put_nowait(update)
#     return "ok", 200

# @app.route("/", methods=["GET"])
# def home():
#     return "Bot is running!", 200
