import os
import requests
from flask import Flask
from threading import Thread
from telegram.ext import Updater, CommandHandler

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CMC_KEY = os.getenv("CMC_API_KEY")
if not TOKEN or not CMC_KEY:
    raise ValueError("TELEGRAM_BOT_TOKEN and CMC_API_KEY must be set.")

app = Flask(__name__)

@app.route("/")
def home():
    return "Altcoin Bot Power Version Running!", 200

COINGECKO_API = "https://api.coingecko.com/api/v3/simple/price"
COINGECKO_GLOBAL = "https://api.coingecko.com/api/v3/global"
CMC_API = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
BINANCE_API = "https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"

COIN_MAP = {
    "SUNDOG": "sundog", "AI16Z": "ai16z", "NEIRO": "neiro", "FET": "fetch-ai",
    "LILPEPE": "lilpepe", "BONK": "bonk", "BIGTIME": "big-time",
    "WIF": "dogwifhat", "PENDLE": "pendle", "ARB": "arbitrum",
    "AERO": "aerodrome-finance", "ADA": "cardano", "DOT": "polkadot",
    "LINK": "chainlink", "AVAX": "avalanche-2", "AAVE": "aave",
    "HBAR": "hedera-hashgraph", "RPL": "rocket-pool", "ZETA": "zetachain",
    "LPT": "livepeer", "SUI": "sui"
}

alerts = {}

def get_coingecko_simple(ids):
    params = {
        "ids": ",".join(ids),
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    resp = requests.get(COINGECKO_API, params=params)
    if resp.status_code != 200:
        return None
    return resp.json()

def get_coingecko_price(coin):
    return get_coingecko_simple([COIN_MAP[coin]])

def get_cmc_price(coin):
    headers = {"X-CMC_PRO_API_KEY": CMC_KEY}
    params = {"symbol": coin.upper(), "convert": "USD,KRW"}
    resp = requests.get(CMC_API, params=params, headers=headers)
    if resp.status_code != 200:
        return None
    data = resp.json()["data"].get(coin.upper())
    if not data:
        return None
    q = data["quote"]
    return {
        "usd": q["USD"]["price"],
        "krw": q["KRW"]["price"],
        "cap": q["USD"]["market_cap"],
        "change": q["USD"]["percent_change_24h"]
    }

def get_binance_price(coin):
    try:
        resp = requests.get(BINANCE_API.format(symbol=coin.upper()))
        if resp.status_code != 200:
            return None
        price = float(resp.json()["price"])
        return price
    except:
        return None

def price_handler(update, context):
    if len(context.args) != 1:
        update.message.reply_text("사용법: /price <코인명>")
        return
    coin = context.args[0].upper()
    if coin not in COIN_MAP:
        update.message.reply_text("🚫 지원되지 않는 코인입니다.")
        return
    cg = get_coingecko_price(coin)
    cmc = get_cmc_price(coin)
    bn = get_binance_price(coin)
    msg = f"💰 {coin} 실시간 데이터\n"
    if cg:
        v = list(cg.values())[0]
        msg += f"[CG] ${v['usd']}, 24H: {v['usd_24h_change']:.2f}%\n"
    else:
        msg += "[CG] 실패\n"
    if cmc:
        msg += f"[CMC] ${cmc['usd']:.2f}, 시총: ${cmc['cap']:,.0f}, 24H: {cmc['change']:.2f}%\n"
    else:
        msg += "[CMC] 실패\n"
    if bn:
        msg += f"[BN] USDT: ${bn:.4f}"
    else:
        msg += "[BN] 실패"
    update.message.reply_text(msg)

def allprices_handler(update, context):
    ids = [COIN_MAP[k] for k in COIN_MAP]
    data = get_coingecko_simple(ids)
    if not data:
        update.message.reply_text("❌ 데이터 조회 실패")
        return
    msg = "💹 전체 코인 가격\n"
    for k, v in COIN_MAP.items():
        d = data.get(v)
        if d:
            msg += f"{k}: ${d['usd']:.3f} | "
    update.message.reply_text(msg.strip(" | "))

def topmovers_handler(update, context):
    ids = [COIN_MAP[k] for k in COIN_MAP]
    data = get_coingecko_simple(ids)
    if not data:
        update.message.reply_text("❌ 데이터 조회 실패")
        return
    movers = sorted(data.items(), key=lambda x: x[1].get("usd_24h_change", 0), reverse=True)[:3]
    msg = "🚀 Top 3 Movers 24H\n"
    for k, v in movers:
        name = next((n for n, id in COIN_MAP.items() if id == k), k)
        msg += f"{name}: {v['usd_24h_change']:.2f}%\n"
    update.message.reply_text(msg)

def summary_handler(update, context):
    resp = requests.get(COINGECKO_GLOBAL)
    if resp.status_code != 200:
        update.message.reply_text("❌ Global 데이터 실패")
        return
    d = resp.json()["data"]
    dom = d["market_cap_percentage"]["btc"]
    cap = d["total_market_cap"]["usd"]
    msg = f"🌐 Market Summary\nBTC Dominance: {dom:.2f}%\nTotal Cap: ${cap:,.0f}"
    update.message.reply_text(msg)

def alerts_handler(update, context):
    if len(context.args) != 2:
        update.message.reply_text("사용법: /alerts <코인> <목표USD>")
        return
    coin, target = context.args[0].upper(), context.args[1]
    if coin not in COIN_MAP:
        update.message.reply_text("🚫 지원되지 않는 코인")
        return
    try:
        target = float(target)
        alerts[coin] = target
        update.message.reply_text(f"🔔 {coin} 알림 설정: ${target}")
    except:
        update.message.reply_text("❌ 숫자 입력 오류")

def alert_checker():
    while True:
        if alerts:
            data = get_coingecko_simple([COIN_MAP[c] for c in alerts])
            for c in list(alerts.keys()):
                v = data.get(COIN_MAP[c], {}).get("usd")
                if v and v >= alerts[c]:
                    print(f"알림: {c} {v} >= {alerts[c]}")
        import time; time.sleep(60)

def start_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("✅ Power Bot!")))
    dp.add_handler(CommandHandler("price", price_handler))
    dp.add_handler(CommandHandler("allprices", allprices_handler))
    dp.add_handler(CommandHandler("topmovers", topmovers_handler))
    dp.add_handler(CommandHandler("summary", summary_handler))
    dp.add_handler(CommandHandler("alerts", alerts_handler))

    Thread(target=alert_checker).start()
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    Thread(target=start_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))