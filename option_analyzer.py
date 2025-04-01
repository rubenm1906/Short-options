# option_analyzer.py
import logging
import pandas as pd
from data_fetcher import get_ticker_iv, get_option_data

logger = logging.getLogger(__name__)

def analyze_ticker(ticker, config):
    """
    Analiza un ticker: verifica IV y obtiene las mejores opciones PUT.
    """
    try:
        # Verificar IV del ticker
        ticker_data = get_ticker_iv(ticker, config)
        if ticker_data is None:
            logger.info(f"{ticker}: Descartado por falta de datos o filtros de IV/precio/volumen")
            return []
        if ticker_data["implied_volatility"] < config["MIN_IV"]:
            logger.info(f"{ticker}: Descartado por IV baja: {ticker_data['implied_volatility']:.2f}% < {config['MIN_IV']}%")
            return []

        # Obtener datos de opciones
        options = get_option_data(ticker, config)
        if not options:
            logger.info(f"{ticker}: No se encontraron opciones que cumplan los criterios")
            return []

        # Ordenar por rentabilidad y distancia del strike
        df = pd.DataFrame(options)
        df = df.sort_values(by=["rentabilidad_anual", "strike_distance"], ascending=[False, False])
        top_options = df.head(config["TOP_CONTRATOS_PER_TICKER"]).to_dict('records')
        logger.info(f"{ticker}: Se seleccionaron {len(top_options)} contratos")
        return top_options
    except Exception as e:
        logger.error(f"Error analizando {ticker}: {e}")
        return []
