# data_fetcher.py
import yfinance as yf
import logging
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

def get_ticker_iv(ticker, config):
    """
    Calcula la volatilidad implícita promedio del ticker usando opciones ATM.
    """
    try:
        stock = yf.Ticker(ticker)
        current_price = stock.info.get('regularMarketPrice', stock.info.get('previousClose', 0))
        volume = stock.info.get('averageVolume', 0)
        if current_price <= 0:
            logger.info(f"{ticker}: Precio actual no válido: ${current_price}")
            return None
        if current_price > config["MAX_STOCK_PRICE"]:
            logger.info(f"{ticker}: Precio actual ${current_price:.2f} excede el máximo de ${config['MAX_STOCK_PRICE']}")
            return None
        if volume < config["MIN_VOLUME_STOCK"]:
            logger.info(f"{ticker}: Volumen promedio {volume} < {config['MIN_VOLUME_STOCK']}")
            return None

        expirations = stock.options
        if not expirations:
            logger.info(f"{ticker}: No hay fechas de vencimiento disponibles para opciones")
            return None

        iv_values = []
        for expiration in expirations:
            expiration_date = datetime.strptime(expiration, '%Y-%m-%d')
            days_to_expiration = (expiration_date - datetime.now()).days
            if days_to_expiration < config["MIN_DIAS_VENCIMIENTO"] or days_to_expiration > config["MAX_DIAS_VENCIMIENTO"]:
                continue

            opt = stock.option_chain(expiration)
            for chain in [opt.puts, opt.calls]:
                if chain.empty:
                    continue
                chain['strike_diff'] = abs(chain['strike'] - current_price)
                atm_option = chain.loc[chain['strike_diff'].idxmin()]
                iv = atm_option.get('impliedVolatility', 0) * 100
                if iv > 0:
                    iv_values.append(iv)

        if not iv_values:
            logger.info(f"{ticker}: No se encontraron opciones válidas para calcular IV")
            return None

        avg_iv = np.mean(iv_values)
        logger.info(f"{ticker}: Volatilidad implícita promedio: {avg_iv:.2f}%")
        return {
            "ticker": ticker,
            "current_price": current_price,
            "volume": volume,
            "implied_volatility": avg_iv
        }
    except Exception as e:
        logger.error(f"Error obteniendo IV para {ticker}: {e}")
        return None

def get_option_data(ticker, config):
    """
    Obtiene datos de opciones PUT para un ticker.
    """
    try:
        stock = yf.Ticker(ticker)
        current_price = stock.info.get('regularMarketPrice', stock.info.get('previousClose', 0))
        if current_price <= 0:
            raise ValueError(f"Precio actual de {ticker} no válido: ${current_price}")
        logger.info(f"Precio actual de {ticker}: ${current_price:.2f}")

        expirations = stock.options
        options_data = []

        for expiration in expirations:
            expiration_date = datetime.strptime(expiration, '%Y-%m-%d')
            days_to_expiration = (expiration_date - datetime.now()).days
            if days_to_expiration < config["MIN_DIAS_VENCIMIENTO"] or days_to_expiration > config["MAX_DIAS_VENCIMIENTO"]:
                logger.debug(f"Expiración {expiration} descartada: {days_to_expiration} días")
                continue

            opt = stock.option_chain(expiration)
            chain = opt.puts
            for _, row in chain.iterrows():
                strike = row['strike']
                bid = row.get('bid', 0)
                last_price = row.get('lastPrice', 0)
                volume = row.get('volume', 0) or 0
                open_interest = row.get('openInterest', 0) or 0
                delta = row.get('delta', 0)
                iv = row.get('impliedVolatility', 0) * 100

                # Filtrar opciones OTM
                if strike >= current_price:
                    continue

                # Filtrar strike al menos 5% por debajo del precio actual
                strike_distance = (current_price - strike) / current_price
                if strike_distance < config["MIN_STRIKE_DISTANCE"]:
                    continue

                # Filtros básicos
                if bid < config["MIN_BID"]:
                    continue
                if last_price <= 0:
                    continue
                if volume < config["MIN_VOLUMEN"]:
                    continue
                if open_interest < config["MIN_OPEN_INTEREST"]:
                    continue
                if not (config["TARGET_DELTA_MIN"] <= delta <= config["TARGET_DELTA_MAX"]):
                    continue

                # Calcular rentabilidad
                rentabilidad_diaria = (last_price * 100) / current_price
                rentabilidad_anual = rentabilidad_diaria * (365 / days_to_expiration)
                if rentabilidad_anual < config["MIN_RENTABILIDAD_ANUAL"]:
                    continue

                # Calcular riesgo
                max_loss = strike * 100
                premium_received = last_price * 100
                net_risk = max_loss - premium_received
                max_risk_allowed = config["CAPITAL"] * config["MAX_RISK_PER_TRADE"]
                if net_risk > max_risk_allowed:
                    continue

                options_data.append({
                    "ticker": ticker,
                    "strike": strike,
                    "expiration": expiration,
                    "days_to_expiration": days_to_expiration,
                    "bid": bid,
                    "last_price": last_price,
                    "volume": volume,
                    "open_interest": open_interest,
                    "rentabilidad_anual": rentabilidad_anual,
                    "delta": delta,
                    "net_risk": net_risk,
                    "implied_volatility": iv,
                    "strike_distance": strike_distance
                })

        logger.info(f"Se encontraron {len(options_data)} opciones para {ticker}")
        return options_data
    except Exception as e:
        logger.error(f"Error obteniendo datos para {ticker}: {e}")
        return []
