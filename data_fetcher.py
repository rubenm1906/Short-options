# data_fetcher.py
import yfinance as yf
import logging
import numpy as np
from datetime import datetime

# Configurar logging para mostrar en consola
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_ticker_iv(ticker, config):
    """
    Calcula la volatilidad implícita promedio del ticker usando opciones ATM.
    """
    try:
        logger.info(f"Obteniendo IV para {ticker}...")
        stock = yf.Ticker(ticker)
        logger.debug(f"Obteniendo información del ticker {ticker}...")
        current_price = stock.info.get('regularMarketPrice', stock.info.get('previousClose', 0))
        volume = stock.info.get('averageVolume', 0)

        # Verificar precio y volumen del subyacente
        if current_price <= 0:
            logger.info(f"{ticker}: Descartado - Precio actual no válido: ${current_price}")
            return None
        if current_price > config["MAX_STOCK_PRICE"]:
            logger.info(f"{ticker}: Descartado - Precio actual ${current_price:.2f} excede el máximo de ${config['MAX_STOCK_PRICE']}")
            return None
        if volume < config["MIN_VOLUME_STOCK"]:
            logger.info(f"{ticker}: Descartado - Volumen promedio {volume} < {config['MIN_VOLUME_STOCK']}")
            return None

        logger.debug(f"{ticker}: Precio actual: ${current_price:.2f}, Volumen promedio: {volume}")

        expirations = stock.options
        if not expirations:
            logger.info(f"{ticker}: Descartado - No hay fechas de vencimiento disponibles para opciones")
            return None

        iv_values = []
        logger.debug(f"Procesando {len(expirations)} fechas de vencimiento para {ticker}...")
        for expiration in expirations:
            expiration_date = datetime.strptime(expiration, '%Y-%m-%d')
            days_to_expiration = (expiration_date - datetime.now()).days
            if days_to_expiration > config["MAX_DIAS_VENCIMIENTO"]:
                logger.debug(f"{ticker}: Expiración {expiration} descartada: {days_to_expiration} días (excede el máximo de {config['MAX_DIAS_VENCIMIENTO']})")
                continue

            logger.debug(f"Obteniendo cadena de opciones para {ticker} con vencimiento {expiration}...")
            opt = stock.option_chain(expiration)
            for chain in [opt.puts, opt.calls]:
                if chain.empty:
                    logger.debug(f"{ticker}: Cadena de opciones vacía para {expiration}")
                    continue
                chain['strike_diff'] = abs(chain['strike'] - current_price)
                atm_option = chain.loc[chain['strike_diff'].idxmin()]
                iv = atm_option.get('impliedVolatility', 0) * 100
                if iv > 0:
                    iv_values.append(iv)
                    logger.debug(f"{ticker}: IV de opción ATM para {expiration}: {iv:.2f}%")
                else:
                    logger.debug(f"{ticker}: IV no válida para {expiration}: {iv}%")

        if not iv_values:
            logger.info(f"{ticker}: Descartado - No se encontraron opciones válidas para calcular IV")
            return None

        avg_iv = np.mean(iv_values)
        logger.info(f"{ticker}: Volatilidad implícita promedio calculada: {avg_iv:.2f}%")
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
        logger.info(f"Obteniendo datos de opciones para {ticker}...")
        stock = yf.Ticker(ticker)
        logger.debug(f"Obteniendo precio actual de {ticker}...")
        current_price = stock.info.get('regularMarketPrice', stock.info.get('previousClose', 0))
        previous_close = stock.info.get('previousClose', 0)  # Obtener el precio del último cierre
        if current_price <= 0:
            logger.info(f"{ticker}: Descartado - Precio actual no válido: ${current_price}")
            raise ValueError(f"Precio actual de {ticker} no válido: ${current_price}")
        logger.info(f"Precio actual de {ticker}: ${current_price:.2f}, Último cierre: ${previous_close:.2f}")

        expirations = stock.options
        options_data = []
        discarded_reasons = {
            "otm": 0,
            "strike_distance": 0,
            "bid": 0,
            "last_price": 0,
            "last_price_too_low": 0,
            "volume": 0,
            "open_interest": 0,
            "delta": 0,
            "delta_invalid": 0,
            "rentabilidad_anual": 0,
            "net_risk": 0,
            "days_to_expiration": 0
        }

        logger.debug(f"Procesando {len(expirations)} fechas de vencimiento para opciones de {ticker}...")
        for expiration in expirations:
            expiration_date = datetime.strptime(expiration, '%Y-%m-%d')
            days_to_expiration = (expiration_date - datetime.now()).days
            if days_to_expiration > config["MAX_DIAS_VENCIMIENTO"]:
                logger.debug(f"Expiración {expiration} descartada: {days_to_expiration} días (excede el máximo de {config['MAX_DIAS_VENCIMIENTO']})")
                discarded_reasons["days_to_expiration"] += 1
                continue

            logger.debug(f"Procesando opciones para {ticker} con vencimiento {expiration} ({days_to_expiration} días)")
            opt = stock.option_chain(expiration)
            chain = opt.puts
            logger.debug(f"Se encontraron {len(chain)} opciones PUT para {expiration}")
            for _, row in chain.iterrows():
                strike = row['strike']
                bid = row.get('bid', 0)
                last_price = row.get('lastPrice', 0)
                volume = row.get('volume', 0) or 0
                open_interest = row.get('openInterest', 0) or 0
                delta = row.get('delta', 0)
                iv = row.get('impliedVolatility', 0) * 100

                # Log para verificar el valor crudo de delta
                logger.debug(f"Opción: Strike ${strike:.2f}, Delta crudo: {row.get('delta', 'No disponible')}")

                # Filtrar opciones OTM
                if strike >= current_price:
                    logger.debug(f"Opción descartada: Strike ${strike:.2f} >= Precio actual ${current_price:.2f} (no es OTM)")
                    discarded_reasons["otm"] += 1
                    continue

                # Filtrar strike al menos 5% por debajo del precio actual
                strike_distance = (current_price - strike) / current_price
                if strike_distance < config["MIN_STRIKE_DISTANCE"]:
                    logger.debug(f"Opción descartada: Distancia del strike {strike_distance*100:.2f}% < {config['MIN_STRIKE_DISTANCE']*100}%")
                    discarded_reasons["strike_distance"] += 1
                    continue

                # Filtros básicos
                if bid < config["MIN_BID"]:
                    logger.debug(f"Opción descartada: Bid ${bid:.2f} < {config['MIN_BID']}")
                    discarded_reasons["bid"] += 1
                    continue
                if last_price <= 0:
                    logger.debug(f"Opción descartada: Último precio ${last_price:.2f} <= 0")
                    discarded_reasons["last_price"] += 1
                    continue
                if last_price < 1.0:
                    logger.debug(f"Opción descartada: Prima ${last_price:.2f} < $1.00")
                    discarded_reasons["last_price_too_low"] += 1
                    continue
                if volume < config["MIN_VOLUMEN"]:
                    logger.debug(f"Opción descartada: Volumen {volume} < {config['MIN_VOLUMEN']}")
                    discarded_reasons["volume"] += 1
                    continue
                if open_interest < config["MIN_OPEN_INTEREST"]:
                    logger.debug(f"Opción descartada: Interés abierto {open_interest} < {config['MIN_OPEN_INTEREST']}")
                    discarded_reasons["open_interest"] += 1
                    continue
                if delta == 0 or delta is None:
                    logger.debug(f"Opción descartada: Delta no válido: {delta}")
                    discarded_reasons["delta_invalid"] += 1
                    continue
                if not (config["TARGET_DELTA_MIN"] <= delta <= config["TARGET_DELTA_MAX"]):
                    logger.debug(f"Opción descartada: Delta {delta:.2f} fuera del rango {config['TARGET_DELTA_MIN']} a {config['TARGET_DELTA_MAX']}")
                    discarded_reasons["delta"] += 1
                    continue

                # Calcular rentabilidad
                rentabilidad_diaria = (last_price * 100) / current_price
                rentabilidad_anual = rentabilidad_diaria * (365 / days_to_expiration)
                if rentabilidad_anual < config["MIN_RENTABILIDAD_ANUAL"]:
                    logger.debug(f"Opción descartada: Rentabilidad anual {rentabilidad_anual:.2f}% < {config['MIN_RENTABILIDAD_ANUAL']}%")
                    discarded_reasons["rentabilidad_anual"] += 1
                    continue

                # Calcular riesgo
                max_loss = strike * 100
                premium_received = last_price * 100
                net_risk = max_loss - premium_received
                max_risk_allowed = config["CAPITAL"] * config["MAX_RISK_PER_TRADE"]
                if net_risk > max_risk_allowed:
                    logger.debug(f"Opción descartada: Riesgo neto ${net_risk:.2f} > ${max_risk_allowed:.2f}")
                    discarded_reasons["net_risk"] += 1
                    continue

                logger.debug(f"Opción válida encontrada: Strike ${strike:.2f}, Rentabilidad anual {rentabilidad_anual:.2f}%, Delta {delta:.2f}, IV {iv:.2f}%")
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
                    "strike_distance": strike_distance,
                    "previous_close": previous_close
                })

        logger.info(f"Se encontraron {len(options_data)} opciones válidas para {ticker}")
        logger.info(f"Motivos de descarte para {ticker}: {discarded_reasons}")
        return options_data
    except Exception as e:
        logger.error(f"Error obteniendo datos para {ticker}: {e}")
        return []
