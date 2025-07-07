
import os
import time
import logging
import requests

from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("✅ Bot is alive!")

def price(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        update.message.reply_text("사용법: /price <코인심볼>")
        return

    symbol = context.args[0].lower()
    try:
        response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd")
        data = response.json()
        if symbol in data:
            price = data[symbol]["usd"]
            update.message.reply_text(f"💰 {symbol.upper()} 가격: ${price}")
        else:
            update.message.reply_text("❌ 코인 정보를 찾을 수 없습니다.")
    except Exception as e:
        logger.error(e)
        update.message.reply_text("❌ 데이터 조회 실패")

def main():
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN 환경변수 누락")
        return

    bot = Bot(TOKEN)
    updater = Updater(bot=bot, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("price", price))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
