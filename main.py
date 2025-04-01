# main.py
import logging
from config import GROUPS_CONFIG
from option_analyzer import analyze_ticker
from discord_notifier import send_discord_notification

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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

        best_contracts_by_ticker = {}
        for ticker in tickers:
            options = analyze_ticker(ticker, config)
            best_contracts_by_ticker[ticker] = options

        send_discord_notification(best_contracts_by_ticker, webhook_url, description)
        logger.info(f"Grupo {group_name} procesado exitosamente")
    except Exception as e:
        logger.error(f"Error procesando grupo {group_name}: {e}")

def main():
    logger.info("Iniciando script para short PUT...")
    for group_name, group_config in GROUPS_CONFIG.items():
        process_group(group_name, group_config)
    logger.info("Script finalizado.")

if __name__ == "__main__":
    main()
