import os
import requests
import logging
from flask import Flask
from threading import Thread
from telegram.ext import Updater, CommandHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set.")

app = Flask(__name__)

@app.route("/")
def home():
    return "Altcoin Diagnostic Bot Running!", 200

COIN_MAP = {
    "SUNDOG": "sundog", "AI16Z": "ai16z", "NEIRO": "neiro", "FET": "fetch-ai",
    "LILPEPE": "lilpepe", "BONK": "bonk", "BIGTIME": "big-time",
    "WIF": "dogwifhat", "PENDLE": "pendle", "ARB": "arbitrum",
    "AERO": "aerodrome-finance", "ADA": "cardano", "DOT": "polkadot",
    "LINK": "chainlink", "AVAX": "avalanche-2", "AAVE": "aave",
    "HBAR": "hedera-hashgraph", "RPL": "rocket-pool", "ZETA": "zetachain",
    "LPT": "livepeer", "SUI": "sui"
}

def get_coingecko_price(coin_id):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": coin_id,
        "vs_currencies": "usd,krw",
        "include_24hr_change": "true"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            logger.warning(f"API 실패 상태 코드: {resp.status_code}")
            return None
        logger.info(f"API 성공 응답: {resp.json()}")
        return resp.json().get(coin_id)
    except Exception as e:
        logger.error(f"API 호출 예외: {e}")
        return None

def price_handler(update, context):
    logger.info(f"/price 명령어 수신: {context.args}")
    if len(context.args) != 1:
        update.message.reply_text("사용법: /price <코인명>")
        return
    coin = context.args[0].upper()
    coin_id = COIN_MAP.get(coin)
    if not coin_id:
        update.message.reply_text("🚫 지원되지 않는 코인입니다.")
        return
    data = get_coingecko_price(coin_id)
    if not data:
        update.message.reply_text("❌ 데이터 조회 실패")
        return
    usd = data["usd"]
    krw = data["krw"]
    change = data["usd_24h_change"]
    msg = f"💰 {coin} 가격\nUSD: ${usd:,}\nKRW: ₩{krw:,}\n24H: {change:.2f}%"
    update.message.reply_text(msg)

def start_handler(update, context):
    logger.info("/start 명령어 수신")
    update.message.reply_text("✅ Altcoin Diagnostic Bot Ready!")

def start_bot():
    logger.info("Bot polling 시작")
    updater = Updater(TOKEN, use_context=True, request_kwargs={"read_timeout": 10, "connect_timeout": 10})
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_handler))
    dp.add_handler(CommandHandler("price", price_handler))

    updater.start_polling(poll_interval=10)
    updater.idle()

if __name__ == "__main__":
    Thread(target=start_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))