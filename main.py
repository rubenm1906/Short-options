# main.py
import logging
import sys
import traceback
from config import GROUPS_CONFIG
from option_analyzer import analyze_ticker
from discord_notifier import send_discord_notification

# Configurar logging para mostrar en consola
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_group(group_name, group_config):
    """
    Procesa un grupo de tickers y envía notificaciones a Discord.
    """
    try:
        logger.info(f"Procesando grupo: {group_name}")
        tickers = group_config["tickers"]
        description = group_config["description"]
        webhook_url = group_config["webhook"]
        config = group_config["config"]

        logger.info(f"Total de tickers a procesar: {len(tickers)}")
        best_contracts_by_ticker = {}
        processed_tickers = 0
        tickers_with_contracts = 0

        for ticker in tickers:
            logger.info(f"Procesando ticker {ticker} ({processed_tickers + 1}/{len(tickers)})...")
            options = analyze_ticker(ticker, config)
            best_contracts_by_ticker[ticker] = options
            processed_tickers += 1
            if options:
                tickers_with_contracts += 1
                logger.info(f"{ticker}: Encontrados {len(options)} contratos")
            else:
                logger.info(f"{ticker}: No se encontraron contratos")

        total_contracts = sum(len(contracts) for contracts in best_contracts_by_ticker.values())
        logger.info(f"Resumen para {group_name}: {tickers_with_contracts}/{processed_tickers} tickers con contratos, {total_contracts} contratos en total")
        send_discord_notification(best_contracts_by_ticker, webhook_url, description)
        logger.info(f"Grupo {group_name} procesado exitosamente")
    except Exception as e:
        logger.error(f"Error procesando grupo {group_name}: {e}")
        logger.error(traceback.format_exc())

def main():
    try:
        # Mensaje inicial para confirmar que el script comienza
        print("Script iniciado - Configurando logging...")
        logger.info("Iniciando script para short PUT...")
        
        total_groups = len(GROUPS_CONFIG)
        processed_groups = 0

        for group_name, group_config in GROUPS_CONFIG.items():
            logger.info(f"Procesando grupo {group_name} ({processed_groups + 1}/{total_groups})...")
            process_group(group_name, group_config)
            processed_groups += 1

        logger.info(f"Script finalizado. Procesados {processed_groups}/{total_groups} grupos.")
    except Exception as e:
        logger.error(f"Error fatal en el script: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
