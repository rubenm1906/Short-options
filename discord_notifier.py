# discord_notifier.py
import requests
import logging

logger = logging.getLogger(__name__)

def send_discord_notification(best_contracts_by_ticker, webhook_url, group_description):
    """
    Envía notificaciones a Discord con los mejores contratos por ticker.
    """
    try:
        if not webhook_url or webhook_url == "URL_POR_DEFECTO":
            logger.error(f"Error: Webhook inválido: {webhook_url}")
            return

        if not best_contracts_by_ticker:
            message = f"No se encontraron contratos para {group_description}."
            payload = {"content": message}
            requests.post(webhook_url, json=payload)
            logger.info("Notificación enviada a Discord (sin contratos)")
            return

        message = f"Mejores contratos para {group_description}:\n"
        for ticker, contracts in best_contracts_by_ticker.items():
            if not contracts:
                continue
            message += f"\n**{ticker}**:\n"
            for contract in contracts:
                message += (f"- Strike: ${contract['strike']:.2f} | "
                           f"Vencimiento: {contract['expiration']} ({contract['days_to_expiration']} días) | "
                           f"Prima: ${contract['last_price']:.2f} | "
                           f"Rent. Anual: {contract['rentabilidad_anual']:.2f}% | "
                           f"Delta: {contract['delta']:.2f} | "
                           f"IV: {contract['implied_volatility']:.2f}% | "
                           f"Distancia: {contract['strike_distance']*100:.2f}% | "
                           f"Riesgo: ${contract['net_risk']:.2f}\n")

        # Discord tiene un límite de 2000 caracteres por mensaje
        if len(message) > 2000:
            messages = [message[i:i+1900] for i in range(0, len(message), 1900)]
        else:
            messages = [message]

        for msg in messages:
            payload = {"content": msg}
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
        logger.info("Notificación enviada a Discord")
    except Exception as e:
        logger.error(f"Error enviando notificación a Discord: {e}")
