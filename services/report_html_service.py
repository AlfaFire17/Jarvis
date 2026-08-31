import os
import html
from datetime import datetime
from core.logger import logger
from core.config import Config

# Días y meses en español para la cabecera
WEEKDAYS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MONTHS_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]

class ReportHTMLService:
    """
    Generador del informe diario HTML responsivo con estética de dossier personal A.L.F.A.
    """
    def generate_report(self, calendar_data, email_data, news_data, crypto_data, target_date=None):
        """
        Construye y guarda de forma atómica el informe HTML en data/reports/alfa-informe-YYYY-MM-DD.html.
        """
        now = datetime.now()
        date_str = target_date or now.strftime("%Y-%m-%d")
        
        filename = f"alfa-informe-{date_str}.html"
        output_dir = Config.REPORTS_DIR
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, filename)
        tmp_path = output_path + ".tmp"

        full_date_es = self._format_date_spanish(now)
        gen_time_str = now.strftime("%H:%M")

        html_content = self._build_html(
            full_date_es=full_date_es,
            gen_time_str=gen_time_str,
            calendar_data=calendar_data,
            email_data=email_data,
            news_data=news_data,
            crypto_data=crypto_data
        )

        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            # Atomic replace
            os.replace(tmp_path, output_path)
            logger.info(f"Informe HTML generado correctamente en: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error escribiendo informe HTML: {e}")
            return None

    def _format_date_spanish(self, dt):
        weekday = WEEKDAYS_ES[dt.weekday()]
        day = dt.day
        month = MONTHS_ES[dt.month - 1]
        year = dt.year
        return f"{weekday}, {day} de {month} de {year}"

    def _build_html(self, full_date_es, gen_time_str, calendar_data, email_data, news_data, crypto_data):
        calendar_html = self._render_calendar_section(calendar_data)
        email_html = self._render_email_section(email_data)
        news_html = self._render_news_section(news_data)
        crypto_html = self._render_crypto_section(crypto_data)

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A.L.F.A. — Informe Diario</title>
    <style>
        :root {{
            --bg-page: #06111F;
            --bg-report: #0A1A2D;
            --bg-section: #0D223A;
            --alfa-red: #FF334D;
            --alfa-red-glow: #FF5C70;
            --title-gold: #F4C542;
            --text-main: #F3F6FB;
            --text-muted: #9FB0C5;
            --divider: #203B57;
            --positive: #42D392;
            --negative: #FF5B68;
            --badge-bg: #162E4A;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--bg-page);
            color: var(--text-main);
            font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.5;
            padding: 40px 16px;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
        }}

        .dossier-container {{
            width: 100%;
            max-width: 1000px;
            background-color: var(--bg-report);
            border: 1px solid var(--divider);
            border-radius: 12px;
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6), 0 0 1px rgba(255, 51, 77, 0.2);
            padding: 40px;
        }}

        /* Header Header Header */
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--divider);
            margin-bottom: 32px;
            flex-wrap: wrap;
            gap: 16px;
        }}

        .brand-section {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}

        .alpha-symbol {{
            font-size: 46px;
            font-weight: 700;
            color: var(--alfa-red);
            text-shadow: 0 0 12px rgba(255, 51, 77, 0.4);
            line-height: 1;
        }}

        .brand-title {{
            font-size: 24px;
            font-weight: 800;
            letter-spacing: 2px;
            color: var(--alfa-red);
        }}

        .report-subtitle {{
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 1.5px;
            color: var(--text-muted);
            text-transform: uppercase;
        }}

        .header-meta {{
            text-align: right;
        }}

        .date-display {{
            font-size: 16px;
            font-weight: 600;
            color: var(--text-main);
        }}

        .status-line {{
            font-size: 11px;
            letter-spacing: 1px;
            color: var(--title-gold);
            text-transform: uppercase;
            margin-top: 4px;
        }}

        /* Sections */
        .section {{
            margin-bottom: 36px;
        }}

        .section-title {{
            color: var(--title-gold);
            font-size: 15px;
            font-weight: 700;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .section-title::before {{
            content: "";
            display: inline-block;
            width: 4px;
            height: 16px;
            background-color: var(--alfa-red);
            border-radius: 2px;
        }}

        .empty-state {{
            background-color: var(--bg-section);
            border: 1px dashed var(--divider);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            color: var(--text-muted);
            font-size: 14px;
        }}

        /* Calendar Styling */
        .events-grid {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .event-card {{
            background-color: var(--bg-section);
            border: 1px solid var(--divider);
            border-radius: 8px;
            padding: 14px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }}

        .event-card.important {{
            border-left: 3px solid var(--alfa-red);
        }}

        .event-time {{
            font-weight: 700;
            color: var(--text-main);
            font-size: 14px;
            min-width: 100px;
        }}

        .event-details {{
            flex: 1;
        }}

        .event-title {{
            font-size: 14px;
            font-weight: 600;
            color: var(--text-main);
        }}

        .event-sub {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.5px;
            background-color: var(--badge-bg);
            color: var(--text-muted);
        }}

        .badge-red {{
            background-color: rgba(255, 51, 77, 0.15);
            color: var(--alfa-red-glow);
            border: 1px solid rgba(255, 51, 77, 0.3);
        }}

        .badge-gold {{
            background-color: rgba(244, 197, 66, 0.15);
            color: var(--title-gold);
            border: 1px solid rgba(244, 197, 66, 0.3);
        }}

        .badge-green {{
            background-color: rgba(66, 211, 146, 0.15);
            color: var(--positive);
            border: 1px solid rgba(66, 211, 146, 0.3);
        }}

        .upcoming-block {{
            margin-top: 16px;
        }}

        .upcoming-header {{
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1px;
            color: var(--text-muted);
            margin-bottom: 8px;
            text-transform: uppercase;
        }}

        /* Email Styling */
        .email-list {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .email-card {{
            background-color: var(--bg-section);
            border: 1px solid var(--divider);
            border-radius: 8px;
            padding: 14px 18px;
        }}

        .email-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .email-sender {{
            font-size: 13px;
            font-weight: 700;
            color: var(--text-main);
        }}

        .email-subject {{
            font-size: 14px;
            font-weight: 600;
            color: var(--text-main);
            margin-bottom: 4px;
        }}

        .email-snippet {{
            font-size: 12px;
            color: var(--text-muted);
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        /* News Styling */
        .news-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
        }}

        @media (max-width: 768px) {{
            .news-grid {{
                grid-template-columns: 1fr;
            }}
            .dossier-container {{
                padding: 20px;
            }}
            .header {{
                text-align: center;
                flex-direction: column;
                align-items: center;
            }}
            .header-meta {{
                text-align: center;
            }}
        }}

        .news-card {{
            background-color: var(--bg-section);
            border: 1px solid var(--divider);
            border-radius: 8px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: border-color 0.2s ease;
        }}

        .news-card:hover {{
            border-color: rgba(244, 197, 66, 0.4);
        }}

        .news-cat {{
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1px;
            color: var(--title-gold);
            text-transform: uppercase;
            margin-bottom: 6px;
        }}

        .news-title {{
            font-size: 14px;
            font-weight: 600;
            color: var(--text-main);
            margin-bottom: 8px;
            line-height: 1.4;
        }}

        .news-title a {{
            color: inherit;
            text-decoration: none;
        }}

        .news-title a:hover {{
            color: var(--alfa-red-glow);
            text-decoration: underline;
        }}

        .news-summary {{
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 12px;
        }}

        .news-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
            color: var(--text-muted);
            border-top: 1px solid var(--divider);
            padding-top: 8px;
        }}

        .news-source {{
            font-weight: 600;
        }}

        /* Crypto Markets Styling */
        .crypto-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
        }}

        @media (max-width: 600px) {{
            .crypto-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .crypto-card {{
            background-color: var(--bg-section);
            border: 1px solid var(--divider);
            border-radius: 8px;
            padding: 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .crypto-asset {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .crypto-icon {{
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background-color: #142B47;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 14px;
            color: var(--title-gold);
            border: 1px solid var(--divider);
        }}

        .crypto-name {{
            font-size: 15px;
            font-weight: 700;
            color: var(--text-main);
        }}

        .crypto-symbol {{
            font-size: 11px;
            color: var(--text-muted);
        }}

        .crypto-prices {{
            text-align: right;
        }}

        .price-eur {{
            font-size: 16px;
            font-weight: 700;
            color: var(--text-main);
        }}

        .price-usd {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        .change-pos {{
            color: var(--positive);
            font-weight: 600;
            font-size: 12px;
        }}

        .change-neg {{
            color: var(--negative);
            font-weight: 600;
            font-size: 12px;
        }}

        /* Footer */
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--divider);
            text-align: center;
            font-size: 11px;
            color: var(--text-muted);
            letter-spacing: 0.5px;
        }}
    </style>
</head>
<body>
    <div class="dossier-container">
        <!-- Header -->
        <header class="header">
            <div class="brand-section">
                <div class="alpha-symbol">&alpha;</div>
                <div>
                    <div class="brand-title">A.L.F.A.</div>
                    <div class="report-subtitle">Informe Diario</div>
                </div>
            </div>
            <div class="header-meta">
                <div class="date-display">{html.escape(full_date_es)}</div>
                <div class="status-line">SISTEMA ACTIVO &middot; GENERADO A LAS {html.escape(gen_time_str)}</div>
            </div>
        </header>

        <!-- 1. CALENDARIO -->
        <section class="section">
            <h2 class="section-title">Calendario &amp; Agenda</h2>
            {calendar_html}
        </section>

        <!-- 2. CORREO -->
        <section class="section">
            <h2 class="section-title">Correo Relevante</h2>
            {email_html}
        </section>

        <!-- 3. NOTICIAS -->
        <section class="section">
            <h2 class="section-title">Noticias del Día</h2>
            {news_html}
        </section>

        <!-- 4. CRYPTO -->
        <section class="section">
            <h2 class="section-title">Mercados Crypto</h2>
            {crypto_html}
        </section>

        <!-- Footer -->
        <footer class="footer">
            A.L.F.A. Personal Briefing System &middot; Creado por Pablo Soriano &middot; Confidencial &amp; Privado
        </footer>
    </div>
</body>
</html>
"""

    def _render_calendar_section(self, calendar_data):
        if not calendar_data.get("connected"):
            reason = calendar_data.get("reason", "No conectado")
            return f'<div class="empty-state">Conecta Google Calendar para incluir tu agenda.<br><small>{html.escape(reason)}</small></div>'

        today_events = calendar_data.get("today_events", [])
        upcoming_events = calendar_data.get("upcoming_events", [])

        if not today_events and not upcoming_events:
            return '<div class="empty-state">No tienes eventos pendientes hoy ni en los próximos días.</div>'

        html_out = []

        if today_events:
            html_out.append('<div class="events-grid">')
            for ev in today_events:
                imp_class = "important" if ev.get("is_important") else ""
                badge_class = "badge-red" if ev.get("is_important") else "badge"
                
                summary = html.escape(ev.get("summary", ""))
                time_str = html.escape(ev.get("time_str", ""))
                time_until = html.escape(ev.get("time_until", ""))
                location = html.escape(ev.get("location", ""))

                loc_html = f" &middot; {location}" if location else ""

                html_out.append(f'''
                <div class="event-card {imp_class}">
                    <div class="event-time">{time_str}</div>
                    <div class="event-details">
                        <div class="event-title">{summary}</div>
                        <div class="event-sub">{time_until}{loc_html}</div>
                    </div>
                    <div><span class="{badge_class}">{time_until}</span></div>
                </div>
                ''')
            html_out.append('</div>')
        else:
            html_out.append('<div class="empty-state">No tienes eventos pendientes hoy.</div>')

        if upcoming_events:
            html_out.append('<div class="upcoming-block">')
            html_out.append('<div class="upcoming-header">Próximas Fechas Importantes</div>')
            html_out.append('<div class="events-grid">')
            for ev in upcoming_events[:5]:
                summary = html.escape(ev.get("summary", ""))
                date_disp = html.escape(ev.get("date_display", ""))
                time_until = html.escape(ev.get("time_until", ""))
                badge_class = "badge-gold" if ev.get("is_important") else "badge"

                html_out.append(f'''
                <div class="event-card">
                    <div class="event-time" style="color: var(--title-gold);">{date_disp}</div>
                    <div class="event-details">
                        <div class="event-title">{summary}</div>
                    </div>
                    <div><span class="{badge_class}">{time_until}</span></div>
                </div>
                ''')
            html_out.append('</div></div>')

        return "".join(html_out)

    def _render_email_section(self, email_data):
        if not email_data.get("connected"):
            reason = email_data.get("reason", "No conectado")
            return f'<div class="empty-state">Conecta Gmail para incluir correo relevante.<br><small>{html.escape(reason)}</small></div>'

        messages = email_data.get("messages", [])
        if not messages:
            return '<div class="empty-state">No se han encontrado correos relevantes recientes.</div>'

        html_out = ['<div class="email-list">']
        for msg in messages:
            subject = html.escape(msg.get("subject", ""))
            sender_name = html.escape(msg.get("sender_name", ""))
            snippet = html.escape(msg.get("snippet", ""))
            date_disp = html.escape(msg.get("date_display", ""))
            category = html.escape(msg.get("category", "Relevante"))
            priority = msg.get("priority", "relevant")
            
            badge_class = "badge-red" if priority == "high" else "badge-gold"

            link = msg.get("link", "#")

            html_out.append(f'''
            <div class="email-card">
                <div class="email-header">
                    <span class="email-sender">{sender_name}</span>
                    <span class="{badge_class}">{category}</span>
                </div>
                <div class="email-subject"><a href="{link}" target="_blank" rel="noopener noreferrer" style="color: inherit; text-decoration: none;">{subject}</a></div>
                <div class="email-snippet">{snippet}</div>
                <div style="font-size: 11px; color: var(--text-muted); margin-top: 6px;">{date_disp}</div>
            </div>
            ''')
        html_out.append('</div>')

        return "".join(html_out)

    def _render_news_section(self, news_data):
        if not news_data.get("available"):
            msg = news_data.get("message", "Noticias no disponibles.")
            return f'<div class="empty-state">{html.escape(msg)}</div>'

        categories_map = news_data.get("categories", {})
        if not categories_map:
            return '<div class="empty-state">Noticias no disponibles durante esta generación.</div>'

        html_out = ['<div class="news-grid">']

        for cat_name, articles in categories_map.items():
            for art in articles:
                title = html.escape(art.get("title", ""))
                summary = html.escape(art.get("summary", ""))
                source = html.escape(art.get("source", ""))
                link = art.get("link", "#")

                html_out.append(f'''
                <div class="news-card">
                    <div>
                        <div class="news-cat">{html.escape(cat_name)}</div>
                        <h3 class="news-title"><a href="{link}" target="_blank" rel="noopener noreferrer">{title}</a></h3>
                        <p class="news-summary">{summary}</p>
                    </div>
                    <div class="news-footer">
                        <span class="news-source">{source}</span>
                        <span>Abrir &rarr;</span>
                    </div>
                </div>
                ''')

        html_out.append('</div>')
        return "".join(html_out)

    def _render_crypto_section(self, crypto_data):
        if not crypto_data.get("available"):
            return '<div class="empty-state">Datos de mercado no disponibles.</div>'

        data = crypto_data.get("data", {})
        if not data:
            return '<div class="empty-state">Datos de mercado no disponibles.</div>'

        updated_at = crypto_data.get("updated_at", "")
        source = crypto_data.get("source", "")

        html_out = ['<div class="crypto-grid">']

        for symbol, asset in data.items():
            name = html.escape(asset.get("name", symbol))
            price_eur = asset.get("price_eur", 0.0)
            price_usd = asset.get("price_usd", 0.0)
            change_24h = asset.get("change_24h", 0.0)

            change_class = "change-pos" if change_24h >= 0 else "change-neg"
            sign = "+" if change_24h >= 0 else ""

            eur_fmt = f"&euro;{price_eur:,.2f}"
            usd_fmt = f"${price_usd:,.2f}"

            html_out.append(f'''
            <div class="crypto-card">
                <div class="crypto-asset">
                    <div class="crypto-icon">{html.escape(symbol)}</div>
                    <div>
                        <div class="crypto-name">{name}</div>
                        <div class="crypto-symbol">{html.escape(symbol)} &middot; {html.escape(source)}</div>
                    </div>
                </div>
                <div class="crypto-prices">
                    <div class="price-eur">{eur_fmt}</div>
                    <div class="price-usd">{usd_fmt}</div>
                    <div class="{change_class}">{sign}{change_24h}% (24h)</div>
                </div>
            </div>
            ''')

        html_out.append('</div>')
        if updated_at:
            html_out.append(f'<div style="font-size: 11px; color: var(--text-muted); text-align: right; margin-top: 8px;">Última actualización: {html.escape(updated_at)}</div>')

        return "".join(html_out)
