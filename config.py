# config.py
import os

NASDAQ_100_TICKERS = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA"]

GROUPS_CONFIG = {
    "nasdaq_short_put": {
        "tickers": NASDAQ_100_TICKERS,
        "description": "NASDAQ-100 Short PUT",
        "webhook": os.getenv("DISCORD_WEBHOOK_URL_NASDAQ", "URL_POR_DEFECTO"),
        "config": {
            "MIN_DIAS_VENCIMIENTO": 20,
            "MAX_DIAS_VENCIMIENTO": 45,
            "MIN_RENTABILIDAD_ANUAL": 35.0,
            "TARGET_DELTA_MIN": -0.20,
            "TARGET_DELTA_MAX": 0.0,
            "MIN_VOLUMEN": 1,
            "MIN_OPEN_INTEREST": 1,
            "MIN_BID": 0.30,
            "CAPITAL": 60000,
            "MAX_RISK_PER_TRADE": 0.04,
            "MIN_IV": 35.0,
            "MIN_VOLUME_STOCK": 150000,
            "MAX_STOCK_PRICE": 170.0,
            "MIN_STRIKE_DISTANCE": 0.05,
            "TOP_CONTRATOS_PER_TICKER": 5,
        }
    }
}
