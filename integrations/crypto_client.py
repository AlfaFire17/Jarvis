import json
import time
import urllib.request
from datetime import datetime
from core.logger import logger

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=eur,usd&include_24hr_change=true"
BINANCE_BTC_USD = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
BINANCE_ETH_USD = "https://api.binance.com/api/v3/ticker/24hr?symbol=ETHUSDT"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ALFA-Assistant/1.0"

class CryptoClient:
    """
    Cliente para la consulta de mercado crypto (BTC y ETH en EUR/USD).
    Soporta cache de 10 minutos para evitar rate limits y fallback secundario a Binance.
    """
    def __init__(self):
        self._cache_data = None
        self._cache_timestamp = 0
        self.cache_ttl = 600  # 10 minutos

    def get_crypto_prices(self, force_refresh=False):
        """
        Obtiene los precios actuales y variación 24h para BTC y ETH.
        """
        now_ts = time.time()
        if not force_refresh and self._cache_data and (now_ts - self._cache_timestamp < self.cache_ttl):
            logger.info("Devolviendo precios crypto desde cache interna.")
            return self._cache_data

        # 1. Intentar CoinGecko API
        cg_data = self._fetch_coingecko()
        if cg_data:
            self._cache_data = cg_data
            self._cache_timestamp = now_ts
            return cg_data

        # 2. Intentar Fallback Binance API
        logger.info("CoinGecko no disponible. Intentando fallback con Binance...")
        binance_data = self._fetch_binance_fallback()
        if binance_data:
            self._cache_data = binance_data
            self._cache_timestamp = now_ts
            return binance_data

        # 3. Si todo falla y hay cache vieja, devolver cache con aviso
        if self._cache_data:
            logger.warning("Red/APIs no disponibles. Devolviendo cache antigua de crypto.")
            return self._cache_data

        return {
            "available": False,
            "message": "Datos de mercado no disponibles.",
            "updated_at": "",
            "source": "Ninguna",
            "data": {}
        }

    def _fetch_coingecko(self):
        """Consulta el endpoint simple de CoinGecko."""
        req = urllib.request.Request(COINGECKO_URL, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=5.0) as response:
                payload = json.loads(response.read().decode('utf-8'))

            btc_info = payload.get("bitcoin", {})
            eth_info = payload.get("ethereum", {})

            now_str = datetime.now().strftime("%H:%M")

            return {
                "available": True,
                "message": "OK",
                "updated_at": now_str,
                "source": "CoinGecko API",
                "data": {
                    "BTC": {
                        "name": "Bitcoin",
                        "symbol": "BTC",
                        "price_eur": btc_info.get("eur", 0.0),
                        "price_usd": btc_info.get("usd", 0.0),
                        "change_24h": round(btc_info.get("eur_24h_change", btc_info.get("usd_24h_change", 0.0)), 2)
                    },
                    "ETH": {
                        "name": "Ethereum",
                        "symbol": "ETH",
                        "price_eur": eth_info.get("eur", 0.0),
                        "price_usd": eth_info.get("usd", 0.0),
                        "change_24h": round(eth_info.get("eur_24h_change", eth_info.get("usd_24h_change", 0.0)), 2)
                    }
                }
            }
        except Exception as e:
            logger.warning(f"Error consultando CoinGecko: {e}")
            return None

    def _fetch_binance_fallback(self):
        """Fallback usando Binance public ticker."""
        try:
            req_btc = urllib.request.Request(BINANCE_BTC_USD, headers={"User-Agent": USER_AGENT})
            req_eth = urllib.request.Request(BINANCE_ETH_USD, headers={"User-Agent": USER_AGENT})

            with urllib.request.urlopen(req_btc, timeout=4.0) as res_btc:
                data_btc = json.loads(res_btc.read().decode('utf-8'))
            with urllib.request.urlopen(req_eth, timeout=4.0) as res_eth:
                data_eth = json.loads(res_eth.read().decode('utf-8'))

            # Aproximación EUR/USD (1.08 EUR per USD aprox si no hay ticker directo)
            usd_eur_rate = 0.92

            btc_usd = float(data_btc.get("lastPrice", 0.0))
            btc_change = float(data_btc.get("priceChangePercent", 0.0))

            eth_usd = float(data_eth.get("lastPrice", 0.0))
            eth_change = float(data_eth.get("priceChangePercent", 0.0))

            now_str = datetime.now().strftime("%H:%M")

            return {
                "available": True,
                "message": "OK",
                "updated_at": now_str,
                "source": "Binance API",
                "data": {
                    "BTC": {
                        "name": "Bitcoin",
                        "symbol": "BTC",
                        "price_eur": round(btc_usd * usd_eur_rate, 2),
                        "price_usd": round(btc_usd, 2),
                        "change_24h": round(btc_change, 2)
                    },
                    "ETH": {
                        "name": "Ethereum",
                        "symbol": "ETH",
                        "price_eur": round(eth_usd * usd_eur_rate, 2),
                        "price_usd": round(eth_usd, 2),
                        "change_24h": round(eth_change, 2)
                    }
                }
            }
        except Exception as e:
            logger.warning(f"Error consultando Binance fallback: {e}")
            return None
