
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

logging.basicConfig(level=logging.INFO)

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

SUPPORTED_COINS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "ADA": "cardano",
    "DOT": "polkadot",
    "AVAX": "avalanche-2",
    "AAVE": "aave",
    "LINK": "chainlink",
    "HBAR": "hedera-hashgraph",
    "NEAR": "near",
    "INJ": "injective-protocol",
    "FET": "fetch-ai",
    "RNDR": "render-token",
    "AR": "arweave",
    "TAO": "bittensor",
    "WLD": "worldcoin-wld",
    "TIA": "celestia",
    "PYTH": "pyth-network",
    "JUP": "jupiter-exchange",
    "STRK": "strike",
    "ZETA": "zetachain",
    "AI16Z": "ai16z",  # Placeholder ID
    "BIGTIME": "big-time",
    "SNT": "status",
    "RPL": "rocket-pool",
    "POL": "polygon-ecosystem-token",
    "GRT": "the-graph",
    "AGIX": "singularitynet",
    "OCEAN": "ocean-protocol",
    "CTXC": "cortex",
    "BAND": "band-protocol",
    "TURBO": "turbo",
    "DOGE": "dogecoin",
    "SHIB": "shiba-inu",
    "PEPE": "pepe",
    "FLOKI": "floki",
    "BONK": "bonk",
    "SATS": "sats-ordinals",
    "WIF": "dogwifcoin",
    "MAGA": "maga",
    "MEW": "cat-in-a-dog-world"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Altcoin Raw Diagnostic Bot Ready!")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("사용법: /price <코인명>")
        return

    symbol = context.args[0].upper()
    coin_id = SUPPORTED_COINS.get(symbol)

    if not coin_id:
        await update.message.reply_text("⛔ 지원되지 않는 코인입니다.")
        return

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    try:
        res = requests.get(url)
        data = res.json()
        price = data[coin_id]["usd"]
        await update.message.reply_text(f"💰 {symbol} 현재 가격: ${price}")
    except Exception as e:
        logging.error(f"Error fetching price: {e}")
        await update.message.reply_text("❌ 데이터 조회 실패")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.run_polling()

if __name__ == "__main__":
    main()
