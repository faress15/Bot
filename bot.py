import logging
import os
import json
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

# فعال‌سازی لاگ برای خطایابی بهتر
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- تعریف چالش کدنویسی و تست‌ها ---
# نام تابعی که از کاربر انتظار داریم تعریف کند
EXPECTED_FUNCTION_NAME = "count_substring"

CHALLENGE_DESCRIPTION = f"""
✅ **چالش کدنویسی این هفته**

تابعی در پایتون به نام `{EXPECTED_FUNCTION_NAME}` بنویس که دو رشته `main_str` و `sub_str` را به عنوان ورودی دریافت کرده و تعداد تکرارهای `sub_str` در `main_str` را برگرداند.

❗️ **نکته مهم:** تکرارهای همپوشان (overlapping) نیز باید شمرده شوند.

مثال:
`count_substring("aaaaaa", "aa")` باید عدد `5` را برگرداند.

کد کامل تابع خود را ارسال کن.
"""

# لیست تست کیس‌ها برای ارزیابی کد کاربر
TEST_CASES = [
    {"input": ["golgoli", "gol"], "expected": 2},
    {"input": ["aaaaaa", "aa"], "expected": 5},
    {"input": ["hello", "l"], "expected": 2},
    {"input": ["ababab", "aba"], "expected": 2},
    {"input": ["", "a"], "expected": 0},
    {"input": ["abc", ""], "expected": 4}, # شمارش رشته خالی در رشته به طول n برابر n+1 است
]

WINNERS_FILE = "winners.json"

# --- تعریف مراحل مکالمه ---
AWAITING_CODE = 0

# --- توابع مربوط به ذخیره‌سازی ---
def load_winners():
    if not os.path.exists(WINNERS_FILE):
        return []
    try:
        with open(WINNERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_winner(user):
    winners = load_winners()
    if user.id not in [w['id'] for w in winners]:
        winners.append({'id': user.id, 'full_name': user.full_name, 'username': user.username})
        with open(WINNERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(winners, f, ensure_ascii=False, indent=4)
        return True
    return False

# --- توابع اصلی ربات ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """شروع مکالمه و ارسال صورت مسئله چالش"""
    user = update.effective_user
    await update.message.reply_html(
        rf"سلام {user.mention_html()}! به چالش کدنویسی این هفته خوش آمدی.",
    )
    await update.message.reply_text(CHALLENGE_DESCRIPTION)
    return AWAITING_CODE

async def evaluate_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """کد ارسالی کاربر را دریافت، اجرا و ارزیابی می‌کند"""
    user_code = update.message.text
    user = update.effective_user
    
    execution_context = {}
    try:
        # اجرای کد کاربر در یک دیکشنری محدود برای امنیت بیشتر
        exec(user_code, execution_context)
    except Exception as e:
        await update.message.reply_text(f"❌ کد شما دارای خطای ساختاری (Syntax) است و اجرا نشد:\n`{e}`")
        return ConversationHandler.END

    # بررسی اینکه آیا تابع مورد نظر توسط کاربر تعریف شده است
    if EXPECTED_FUNCTION_NAME not in execution_context or not callable(execution_context[EXPECTED_FUNCTION_NAME]):
        await update.message.reply_text(f"کد شما باید تابعی به نام `{EXPECTED_FUNCTION_NAME}` تعریف کند. لطفاً دوباره تلاش کنید.")
        return ConversationHandler.END
        
    user_function = execution_context[EXPECTED_FUNCTION_NAME]
    
    # اجرای تست کیس‌ها
    for i, test in enumerate(TEST_CASES):
        main_str, sub_str = test["input"]
        expected = test["expected"]
        try:
            actual = user_function(main_str, sub_str)
            if actual != expected:
                await update.message.reply_text(
                    f"❌ تست شماره {i+1} ناموفق بود.\n"
                    f"ورودی: `('{main_str}', '{sub_str}')`\n"
                    f"خروجی مورد انتظار: `{expected}`\n"
                    f"خروجی کد شما: `{actual}`\n\n"
                    "لطفاً کد خود را اصلاح کرده و دوباره با دستور /start تلاش کنید."
                )
                return ConversationHandler.END # پایان مکالمه در صورت شکست
        except Exception as e:
            await update.message.reply_text(
                f"❌ کد شما در حین اجرا روی تست شماره {i+1} با خطا مواجه شد:\n`{e}`\n\n"
                "لطفاً کد خود را اصلاح کرده و دوباره با دستور /start تلاش کنید."
            )
            return ConversationHandler.END

    # اگر تمام تست‌ها موفقیت‌آمیز بود
    await update.message.reply_text("✅ تبریک! کد شما تمام تست‌ها را با موفقیت پشت سر گذاشت.")
    if save_winner(user):
        await update.message.reply_text("نام شما در لیست برندگان این هفته ثبت شد! 🏆")
    else:
        await update.message.reply_text("شما قبلاً در لیست برندگان ثبت شده‌اید.")
        
    return ConversationHandler.END

async def show_winners(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """لیست برندگان را نمایش می‌دهد"""
    winners = load_winners()
    if not winners:
        await update.message.reply_text("هنوز هیچ برنده‌ای در این هفته ثبت نشده است.")
        return

    message = "🏆 **لیست برندگان این هفته** 🏆\n\n"
    for i, winner in enumerate(winners):
        user_display = winner.get('full_name', 'کاربر ناشناس')
        if winner.get('username'):
            user_display += f" (@{winner['username']})"
        message += f"{i+1}. {user_display}\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مکالمه را لغو می‌کند"""
    await update.message.reply_text("چالش لغو شد. برای شروع مجدد /start را بزنید.")
    return ConversationHandler.END

def main() -> None:
    """راه‌اندازی و اجرای ربات"""
    TOKEN = os.environ.get("TOKEN")
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

    if not TOKEN:
        raise ValueError("متغیر TOKEN در تنظیمات رندر یافت نشد.")
    if not WEBHOOK_URL:
        raise ValueError("متغیر WEBHOOK_URL در تنظیمات رندر یافت نشد.")

    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AWAITING_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, evaluate_code)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("winners", show_winners)) # افزودن دستور جدید
    
    port = int(os.environ.get("PORT", 8443))
    
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=f"https://{WEBHOOK_URL}/{TOKEN}"
    )

if __name__ == "__main__":
    main()

