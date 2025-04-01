# config.py
import os

# Lista de tickers del NASDAQ-100 (simplificada para el ejemplo)
NASDAQ_100_TICKERS = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA"]

# Configuración de grupos
GROUPS_CONFIG = {
    "nasdaq_short_put": {
        "tickers": NASDAQ_100_TICKERS,
        "description": "NASDAQ-100 Short PUT",
        "webhook": os.getenv("DISCORD_WEBHOOK_URL_NASDAQ", "URL_POR_DEFECTO"),
        "config": {
            "MIN_DIAS_VENCIMIENTO": 20,
            "MAX_DIAS_VENCIMIENTO": 45,
            "MIN_RENTABILIDAD_ANUAL": 35.0,  # Rentabilidad anualizada mínima
            "TARGET_DELTA_MIN": -0.20,  # Delta para probabilidad de éxito ~80%
            "TARGET_DELTA_MAX": 0.0,
            "MIN_VOLUMEN": 1,
            "MIN_OPEN_INTEREST": 1,
            "MIN_BID": 0.30,
            "CAPITAL": 60000,
            "MAX_RISK_PER_TRADE": 0.04,  # 4% del capital por operación
            "MIN_IV": 35.0,  # Volatilidad implícita mínima del ticker (35%)
            "MIN_VOLUME_STOCK": 150000,  # Volumen promedio diario mínimo del subyacente
            "MAX_STOCK_PRICE": 170.0,  # Precio máximo del subyacente
            "MIN_STRIKE_DISTANCE": 0.05,  # Strike al menos 5% por debajo del precio actual
            "TOP_CONTRATOS_PER_TICKER": 5,  # 5 mejores contratos por ticker
        }
    }
    # Puedes agregar más grupos aquí en el futuro, como "sp500_short_put"
}
