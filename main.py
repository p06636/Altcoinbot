import os
from flask import Flask
from threading import Thread
from telegram.ext import Updater, CommandHandler

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set.")

app = Flask(__name__)

@app.route('/')
def home():
    return "Altcoin Bot is running", 200

def start_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", lambda update, context: update.message.reply_text("✅ Altcoin Bot running (getUpdates + Flask)!")))
    dp.add_handler(CommandHandler("altsignal", lambda update, context: update.message.reply_text("🧭 알트시즌 흐름 모니터링 알림 제공")))
    dp.add_handler(CommandHandler("coinalert", lambda update, context: update.message.reply_text("🪙 고래 활동, 급등락, 일정 알림 제공")))
    dp.add_handler(CommandHandler("strategy", lambda update, context: update.message.reply_text("🔁 진입·익절 전략 도우미 제공")))
    dp.add_handler(CommandHandler("newcoins", lambda update, context: update.message.reply_text("💡 신규/저시총 알트 알림 제공")))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    Thread(target=start_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))