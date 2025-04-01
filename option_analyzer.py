# option_analyzer.py
import logging
import pandas as pd
from data_fetcher import get_ticker_iv, get_option_data

# Configurar logging para mostrar en consola
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_ticker(ticker, config):
    """
    Analiza un ticker: verifica IV y obtiene las mejores opciones PUT.
    """
    try:
        logger.info(f"Analizando {ticker}...")
        # Verificar IV del ticker
        ticker_data = get_ticker_iv(ticker, config)
        if ticker_data is None:
            logger.info(f"{ticker}: No se procesará - Falló la obtención de datos o no cumple con los filtros iniciales")
            return []
        if ticker_data["implied_volatility"] < config["MIN_IV"]:
            logger.info(f"{ticker}: Descartado - IV baja: {ticker_data['implied_volatility']:.2f}% < {config['MIN_IV']}%")
            return []

        # Obtener datos de opciones
        options = get_option_data(ticker, config)
        if not options:
            logger.info(f"{ticker}: No se encontraron opciones que cumplan los criterios")
            return []

        # Ordenar por rentabilidad y distancia del strike
        logger.debug(f"Ordenando {len(options)} opciones para {ticker}...")
        df = pd.DataFrame(options)
        df = df.sort_values(by=["rentabilidad_anual", "strike_distance"], ascending=[False, False])
        top_options = df.head(config["TOP_CONTRATOS_PER_TICKER"]).to_dict('records')

        if top_options:
            logger.info(f"{ticker}: Se seleccionaron {len(top_options)} contratos:")
            for opt in top_options:
                logger.info(f"  - Strike: ${opt['strike']:.2f}, Rentabilidad: {opt['rentabilidad_anual']:.2f}%, Distancia: {opt['strike_distance']*100:.2f}%, Delta: {opt['delta']:.2f}, IV: {opt['implied_volatility']:.2f}%")
        else:
            logger.info(f"{ticker}: No se seleccionaron contratos después de ordenar")

        return top_options
    except Exception as e:
        logger.error(f"Error analizando {ticker}: {e}")
        return []
