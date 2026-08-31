import re
import unicodedata
from core.logger import logger
from integrations.news_provider import NewsProvider

CLICKBAIT_PATTERNS = [
    r"no te creeras", r"no creeras", r"este truco", r"mira lo que",
    r"lo que pasa despues", r"te sorprendera", r"por esta razon",
    r"click aqui", r"haz esto", r"la razon por la que"
]

class NewsService:
    """
    Servicio de curación, filtrado de clickbait y deduplicación de noticias.
    """
    def __init__(self, provider=None):
        self.provider = provider or NewsProvider()

    def get_curated_news(self, max_per_category=2):
        """
        Recopila y filtra las noticias del día agrupadas por categoría.
        """
        try:
            raw_news_map = self.provider.fetch_news_from_feeds(max_per_category=max_per_category*2)
            
            curated_map = {}
            total_count = 0

            for category, articles in raw_news_map.items():
                curated_articles = []
                seen_titles = set()

                for article in articles:
                    title = article["title"]
                    norm_title = self._normalize_str(title)

                    # Filtrar duplicados
                    if norm_title in seen_titles:
                        continue

                    # Filtrar clickbait
                    if self._is_clickbait(norm_title):
                        continue

                    seen_titles.add(norm_title)
                    curated_articles.append(article)

                    if len(curated_articles) >= max_per_category:
                        break

                curated_map[category] = curated_articles
                total_count += len(curated_articles)

            if total_count == 0:
                return {
                    "available": False,
                    "message": "Noticias no disponibles durante esta generación.",
                    "categories": {}
                }

            return {
                "available": True,
                "message": "OK",
                "total_count": total_count,
                "categories": curated_map
            }

        except Exception as e:
            logger.error(f"Error procesando noticias: {e}")
            return {
                "available": False,
                "message": "Noticias no disponibles durante esta generación.",
                "categories": {}
            }

    def _normalize_str(self, text):
        """Normaliza texto para comparación sin acentos ni signos."""
        if not text:
            return ""
        text = text.lower().strip()
        text = ''.join(c for c in unicodedata.normalize('NFD', text)
                      if unicodedata.category(c) != 'Mn')
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def _is_clickbait(self, norm_title):
        """Detecta patrones habituales de amarillismo o clickbait."""
        return any(re.search(pat, norm_title) for pat in CLICKBAIT_PATTERNS)
