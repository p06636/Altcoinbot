
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("🚀 AltSeasonPulseBot이 시작되었습니다!")

def price(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        update.message.reply_text("💡 사용법: /price [코인명]")
        return
    coin = args[0].upper()
    # 모의 데이터 응답
    update.message.reply_text(f"📈 {coin} 현재 가격 (모의): 123.45 USD")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("price", price))
    updater.start_polling()
    print("✅ Bot is polling...")
    updater.idle()

if __name__ == "__main__":
    main()
