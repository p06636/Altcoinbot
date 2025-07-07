
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("✅ Altcoin Diagnostic Bot Ready!\n사용법: /price <코인명>")

def price(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("사용법: /price <코인명>")
        return
    coin = context.args[0].lower()
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        if coin in data:
            price = data[coin]["usd"]
            update.message.reply_text(f"📈 {coin.upper()} 현재 가격: ${price}")
        else:
            update.message.reply_text(f"❌ {coin.upper()} 데이터 없음 (API 응답: {data})")
    except Exception as e:
        update.message.reply_text(f"❌ 데이터 조회 실패: {str(e)}")

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
