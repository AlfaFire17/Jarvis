from core.logger import logger
from integrations.crypto_client import CryptoClient

class MarketService:
    """
    Servicio para empaquetar y estructurar la información del mercado cripto.
    """
    def __init__(self, crypto_client=None):
        self.crypto_client = crypto_client or CryptoClient()

    def get_market_summary(self, force_refresh=False):
        """
        Obtiene los precios de BTC y ETH listos para el informe diario.
        """
        try:
            return self.crypto_client.get_crypto_prices(force_refresh=force_refresh)
        except Exception as e:
            logger.error(f"Error obteniendo resumen de mercados: {e}")
            return {
                "available": False,
                "message": "Datos de mercado no disponibles.",
                "updated_at": "",
                "source": "Ninguna",
                "data": {}
            }
