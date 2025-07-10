from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

TOKEN = "여기에_당신의_텔레그램_토큰_입력"
CMC_API_KEY = "5476857d-f58c-4340-8e95-12c8193705dc"
CMC_API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Altcoin Raw Diagnostic Bot Ready!")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("사용법: /price <코인명>")
        return
    symbol = context.args[0].upper()
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    response = requests.get(CMC_API_URL, headers=headers)
    data = response.json()

    for coin in data.get("data", []):
        if coin["symbol"] == symbol:
            price = coin["quote"]["USD"]["price"]
            await update.message.reply_text(f"{symbol} 현재 가격: ${price:,.4f}")
            return

    await update.message.reply_text("🚫 지원되지 않는 코인입니다.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
