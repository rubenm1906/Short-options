# option_analyzer.py
import logging
from data_fetcher import get_ticker_iv, get_option_data

# Configurar logging para mostrar en consola
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_ticker(ticker, config):
    """
    Analiza un ticker y devuelve las mejores opciones PUT.
    """
    try:
        # Obtener IV del ticker
        ticker_data = get_ticker_iv(ticker, config)
        if not ticker_data:
            logger.info(f"No se analizarán opciones para {ticker} debido a filtros de IV o datos inválidos")
            return []

        # Log detallado de los datos del ticker
        logger.debug(f"Datos del ticker {ticker}: {ticker_data}")

        # Obtener datos de opciones
        options = get_option_data(ticker, config)
        if not options:
            logger.info(f"No se encontraron opciones válidas para {ticker}")
            return []

        # Ordenar opciones por rentabilidad anual descendente
        options.sort(key=lambda x: x["rentabilidad_anual"], reverse=True)

        # Seleccionar las mejores opciones según el límite
        top_options = options[:config["TOP_CONTRATOS_PER_TICKER"]]
        logger.info(f"Se seleccionaron {len(top_options)} de {len(options)} opciones para {ticker}")
        # Log detallado de las opciones seleccionadas
        if top_options:
            logger.debug(f"Opciones seleccionadas para {ticker}:")
            for opt in top_options:
                logger.debug(f"  - Strike ${opt['strike']:.2f}, Vencimiento {opt['expiration']}, Rentabilidad {opt['rentabilidad_anual']:.2f}%, Delta {opt['delta']:.2f}")
        else:
            logger.debug(f"No se seleccionaron opciones para {ticker} después de ordenar")

        return top_options
    except Exception as e:
        logger.error(f"Error analizando ticker {ticker}: {e}")
        return []
