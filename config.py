# config.py
import os

NASDAQ_100_TICKERS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA", "PEP", "COST", "CSCO",
    "TMUS", "CMCSA", "INTC", "AMD", "QCOM", "TXN", "AMGN", "HON", "INTU", "SBUX",
    "GILD", "MDLZ", "ADBE", "NFLX", "PYPL", "ASML", "SNPS", "CDNS", "MRNA", "PANW",
    "REGN", "ADP", "VRTX", "LRCX", "CSX", "MU", "FISV", "BIIB", "KLAC", "AEP",
    "MAR", "ORLY", "KDP", "MNST", "FTNT", "ADSK", "KHC", "ODFL", "MCHP", "IDXX",
    "CTAS", "EXC", "PCAR", "WBA", "ROST", "DXCM", "ILMN", "WBD", "EA", "FAST",
    "VRSK", "CPRT", "BKR", "XEL", "ANSS", "TEAM", "DLTR", "WDAY", "PAYX", "SBAC",
    "CTSH", "VRSN", "SWKS", "MTCH", "INCY", "TTD", "ZM", "SIRI", "NTES", "EBAY",
    "LULU", "ALGN", "JD", "SGEN", "OKTA", "CDW", "ZS", "CHTR", "ULTA", "CINF",
    "NDAQ", "TTWO", "ON", "ENPH", "CEG", "FANG", "GFS", "GEHC"
]

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
