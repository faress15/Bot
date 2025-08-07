from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! بات فعال است.")

async def rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("رتبه‌بندی هنوز آماده نیست.")

async def receive_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("کد شما دریافت شد و در حال بررسی است.")
