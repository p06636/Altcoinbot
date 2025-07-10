import logging
from telegram.ext import Updater, CommandHandler
import requests

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

def start(update, context):
    update.message.reply_text("✅ Altcoin Bot Ready!\n사용법: /price <코인명>")

def price(update, context):
    if len(context.args) != 1:
        update.message.reply_text("❗ 사용법: /price <코인명>")
        return

    coin = context.args[0].lower()
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        if coin in data:
            usd_price = data[coin]['usd']
            update.message.reply_text(f"💰 {coin.upper()} 가격: ${usd_price}")
        else:
            update.message.reply_text("🚫 지원되지 않는 코인입니다.")
    except Exception as e:
        update.message.reply_text("❌ 데이터 조회 실패")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("price", price))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
