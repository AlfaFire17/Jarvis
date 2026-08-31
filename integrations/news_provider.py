import urllib.request
import xml.etree.ElementTree as ET
import html
import re
from datetime import datetime
from core.logger import logger

# Feeds RSS fiables en español e inglés técnico
NEWS_FEEDS = {
    "IA": [
        {"name": "Xataka AI", "url": "https://www.xataka.com/categoria/inteligencia-artificial/rss2.xml"},
        {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
        {"name": "Genbeta AI", "url": "https://www.genbeta.com/categoria/inteligencia-artificial/rss2.xml"}
    ],
    "Informática": [
        {"name": "Hacker News", "url": "https://news.ycombinator.com/rss"},
        {"name": "Xataka Tech", "url": "https://feeds.weblogssl.com/xataka"},
        {"name": "Genbeta", "url": "https://www.genbeta.com/rss2.xml"}
    ],
    "Videojuegos": [
        {"name": "VidaExtra", "url": "https://www.vidaextra.com/rss2.xml"},
        {"name": "3DJuegos", "url": "https://www.3djuegos.com/feed/noticias"}
    ],
    "Cripto": [
        {"name": "CoinTelegraph ES", "url": "https://es.cointelegraph.com/rss"},
        {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/"}
    ],
    "Mercados": [
        {"name": "El Economista", "url": "https://www.eleconomista.es/rss/rss-mercados.php"},
        {"name": "El Mundo Economía", "url": "https://e00-elmundo.uecdn.es/elmundo/rss/economia.xml"}
    ]
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ALFA-Assistant/1.0"

class NewsProvider:
    """
    Proveedor de noticias vía agregación de feeds RSS directos.
    Tolerante a fallos de red y rate limits.
    """
    def fetch_news_from_feeds(self, max_per_category=2):
        """
        Recopila noticias de todas las categorías configuradas.
        """
        results = {}

        for category, feeds in NEWS_FEEDS.items():
            category_articles = []
            for feed_info in feeds:
                try:
                    articles = self._fetch_single_feed(feed_info["name"], feed_info["url"], category)
                    category_articles.extend(articles)
                    if len(category_articles) >= max_per_category * 2:
                        break
                except Exception as e:
                    logger.warning(f"No se pudo cargar feed RSS {feed_info['name']}: {e}")

            results[category] = category_articles

        return results

    def _fetch_single_feed(self, source_name, feed_url, category):
        """Descarga y parsea un feed RSS individual."""
        req = urllib.request.Request(feed_url, headers={"User-Agent": USER_AGENT})
        
        try:
            with urllib.request.urlopen(req, timeout=4.0) as response:
                content = response.read()
                
            root = ET.fromstring(content)
            items = root.findall(".//item")
            if not items:
                # Intentar formato Atom
                items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

            parsed_articles = []
            for item in items[:5]: # Inspeccionar primeros 5 de cada feed
                article = self._parse_rss_item(item, source_name, category)
                if article:
                    parsed_articles.append(article)

            return parsed_articles
        except Exception as e:
            logger.debug(f"Error procesando feed {feed_url}: {e}")
            return []

    def _parse_rss_item(self, item, source_name, category):
        """Extrae titular, enlace, resumen y fecha de un nodo RSS o Atom."""
        try:
            title_elem = item.find("title")
            link_elem = item.find("link")
            desc_elem = item.find("description")
            pub_date_elem = item.find("pubDate")

            if title_elem is None or title_elem.text is None:
                return None

            title = html.unescape(title_elem.text).strip()
            
            # Limpiar etiquetas HTML del título si tuviera
            title = re.sub(r'<[^>]+>', '', title)

            # Obtener link
            link = ""
            if link_elem is not None:
                if link_elem.text:
                    link = link_elem.text.strip()
                elif 'href' in link_elem.attrib:
                    link = link_elem.attrib['href'].strip()

            if not link:
                return None

            # Obtener resumen
            summary = ""
            if desc_elem is not None and desc_elem.text:
                raw_desc = html.unescape(desc_elem.text)
                # Eliminar HTML tags del resumen
                summary = re.sub(r'<[^>]+>', '', raw_desc).strip()
                # Colapsar espacios múltiples
                summary = re.sub(r'\s+', ' ', summary)
                # Recortar a 160 caracteres
                if len(summary) > 160:
                    summary = summary[:157] + "..."

            if not summary:
                summary = f"Noticia publicada en {source_name}."

            pub_date = pub_date_elem.text.strip() if pub_date_elem is not None and pub_date_elem.text else ""

            return {
                "title": title,
                "link": link,
                "summary": summary,
                "source": source_name,
                "category": category,
                "pub_date": pub_date
            }
        except Exception as e:
            return None
