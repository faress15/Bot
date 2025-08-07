import json
import datetime
import requests
from config import BOT_TOKEN, PISTON_URL
from telegram import Update
from telegram.ext import ContextTypes

# بارگذاری سوال فعلی
def load_challenge():
    with open("challenges.json", "r", encoding="utf-8") as f:
        return json.load(f)["current"]

# ذخیره جواب درست
def save_submission(name, code):
    with open("submissions.json", "r+", encoding="utf-8") as f:
        try:
            submissions = json.load(f)
        except json.JSONDecodeError:
            submissions = []
        submissions.append({
            "name": name,
            "code": code,
            "timestamp": datetime.datetime.now().isoformat()
        })
        f.seek(0)
        json.dump(submissions, f, indent=2, ensure_ascii=False)
        f.truncate()

# اجرای کد روی Piston API
def run_code(language, code, func_name, test_cases):
    for case in test_cases:
        inputs = ", ".join([repr(i) for i in case["input"]])
        test_code = f"""{code}\nprint({func_name}({inputs}))"""

        payload = {
            "language": language,
            "version": "3.10.0",
            "files": [
                {
                    "name": "main.py",
                    "content": test_code
                }
            ],
            "stdin": "",
            "args": [],
            "compile_timeout": 10000,
            "run_timeout": 3000
        }

        response = requests.post(PISTON_URL, json=payload)
        result = response.json()

        output = result.get("run", {}).get("stdout", "").strip().splitlines()[-1]
        stderr = result.get("run", {}).get("stderr", "").strip()
        expected = str(case["expected"])

        if output != expected or stderr:
            return False
    return True


# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    challenge = load_challenge()
    
    explanation = (
        f"👋 سلام {update.effective_user.first_name}!\n\n"
        "به چالش هفتگی کدنویسی خوش اومدی! 🧠💻\n\n"
        "📌 سوال این هفته:\n"
        f"{challenge['question']}\n\n"
        "📥 لطفاً تابع خودتو فقط به صورت تابع بنویس (نه کلاس، نه main).\n"
        f"🧪 زبان: {challenge['language']}\n"
        f"📌 تابع باید این نام رو داشته باشه: {challenge['function_name']}\n"
        "📤 بعد از ارسال، بات با چند ورودی تست بررسی می‌کنه اگه درست بود اسمت رو ثبت می‌کنه.\n\n"
        "👀 منتظر کدت هستم! موفق باشی 💪"
    )
    
    await update.message.reply_text(explanation)


# دریافت کد
async def receive_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_code = update.message.text
    user_name = update.message.from_user.full_name
    challenge = load_challenge()
    
    success = run_code(
        challenge["language"], user_code,
        challenge["function_name"], challenge["test_cases"]
    )
    
    if success:
        save_submission(user_name, user_code)
        await update.message.reply_text("✅ آفرین! جواب درسته 🎉 اسمت ثبت شد.")
    else:
        await update.message.reply_text("❌ متاسفم، خروجی درست نبود. دوباره تلاش کن!")

# دستور /rank
async def rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open("submissions.json", "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []

        names = [s["name"] for s in data]
        leaderboard = "\n".join(f"{i+1}. {name}" for i, name in enumerate(sorted(set(names))))
        await update.message.reply_text("🏆 لیست افراد موفق:\n\n" + leaderboard)
