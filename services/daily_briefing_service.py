import os
import subprocess
import webbrowser
from datetime import datetime
from core.logger import logger
from core.config import Config
from integrations.google_calendar_client import GoogleCalendarClient
from integrations.gmail_client import GmailClient
from services.email_prioritizer_service import EmailPrioritizerService
from services.news_service import NewsService
from services.market_service import MarketService
from services.report_html_service import ReportHTMLService

class DailyBriefingService:
    """
    Orquestador principal del Informe Diario de A.L.F.A.
    Coordina la recolección de datos, validación de fecha, persistencia JSON y apertura del HTML.
    """
    def __init__(self, memory_service, calendar_client=None, gmail_client=None,
                 email_prioritizer=None, news_service=None, market_service=None,
                 html_service=None):
        self.memory = memory_service
        self.calendar_client = calendar_client or GoogleCalendarClient()
        self.gmail_client = gmail_client or GmailClient()
        self.email_prioritizer = email_prioritizer or EmailPrioritizerService()
        self.news_service = news_service or NewsService()
        self.market_service = market_service or MarketService()
        self.html_service = html_service or ReportHTMLService()

    def check_and_auto_generate_on_startup(self):
        """
        Ejecuta la comprobación al arranque manual de A.L.F.A.
        SOLO genera y abre el informe si no se ha generado automáticamente hoy.
        """
        settings = self.memory.get_daily_briefing_settings()
        if not settings.get("enabled", True):
            logger.info("Informe diario desactivado en la configuración.")
            return None

        today_str = datetime.now().strftime("%Y-%m-%d")
        briefing_data = self.memory.get_daily_briefing_data()

        if briefing_data.get("last_auto_generated_date") == today_str:
            logger.info(f"Informe diario automático para hoy ({today_str}) ya fue generado previamente. Sistema en silencio.")
            return {
                "success": True,
                "already_generated": True,
                "report_path": briefing_data.get("last_report_path")
            }

        logger.info(f"Primer arranque del día ({today_str}). Generando Informe Diario A.L.F.A....")
        return self.generate_briefing(force=False, mode="automatic_startup", open_browser=settings.get("auto_open_report", True))

    def generate_briefing(self, force=False, mode="manual_command", open_browser=True):
        """
        Genera el informe diario completo recolectando todas las fuentes.
        """
        today_str = datetime.now().strftime("%Y-%m-%d")
        briefing_data = self.memory.get_daily_briefing_data()

        if not force and mode == "automatic_startup" and briefing_data.get("last_auto_generated_date") == today_str:
            return {
                "success": True,
                "already_generated": True,
                "report_path": briefing_data.get("last_report_path")
            }

        logger.info("Recopilando datos para el Informe Diario...")

        # 1. Calendario
        calendar_res = self.calendar_client.get_agenda(days_ahead=14)

        # 2. Correo
        raw_gmail = self.gmail_client.get_recent_messages(lookback_days=3)
        prioritized_emails = self.email_prioritizer.prioritize_emails(raw_gmail.get("messages", []), max_items=10)
        email_res = {
            "connected": raw_gmail.get("connected", False),
            "reason": raw_gmail.get("reason", "OK"),
            "messages": prioritized_emails
        }

        # 3. Noticias
        news_res = self.news_service.get_curated_news(max_per_category=2)

        # 4. Mercados Crypto
        crypto_res = self.market_service.get_market_summary(force_refresh=force)

        # 5. Generar archivo HTML
        report_path = self.html_service.generate_report(
            calendar_data=calendar_res,
            email_data=email_res,
            news_data=news_res,
            crypto_data=crypto_res,
            target_date=today_str
        )

        if not report_path:
            logger.error("No se pudo generar el archivo HTML del informe diario.")
            return {"success": False, "reason": "Error al escribir el archivo HTML."}

        # 6. Actualizar persistencia JSON de forma atómica
        now_iso = datetime.now().astimezone().isoformat()
        updates = {
            "last_generated_at": now_iso,
            "last_report_path": report_path,
            "last_generation_status": "success",
            "report_generation_mode": mode
        }
        if mode == "automatic_startup" or force:
            updates["last_auto_generated_date"] = today_str

        self.memory.update_daily_briefing_data(updates)

        # 7. Abrir informe en navegador si procede
        if open_browser:
            self.open_report(report_path)

        return {
            "success": True,
            "already_generated": False,
            "report_path": report_path,
            "calendar_events_count": len(calendar_res.get("today_events", [])),
            "emails_count": len(prioritized_emails),
            "news_count": news_res.get("total_count", 0)
        }

    def open_report(self, report_path=None):
        """
        Abre el informe diario en el navegador preferido (Opera GX o predeterminado).
        """
        if not report_path:
            briefing_data = self.memory.get_daily_briefing_data()
            report_path = briefing_data.get("last_report_path")

        if not report_path or not os.path.exists(report_path):
            logger.warning("No se encontró ningún informe diario guardado para abrir.")
            return False

        abs_path = os.path.abspath(report_path)
        file_uri = f"file:///{abs_path.replace(os.sep, '/')}"

        # Actualizar timestamp de apertura en JSON
        self.memory.update_daily_briefing_data({"last_opened_at": datetime.now().astimezone().isoformat()})

        # Comprobar navegador preferido / Opera GX
        if Config.OPERA_PATH and os.path.exists(Config.OPERA_PATH):
            try:
                logger.info(f"Abriendo informe en Opera GX: {abs_path}")
                subprocess.Popen([Config.OPERA_PATH, abs_path])
                return True
            except Exception as e:
                logger.warning(f"No se pudo abrir con Opera GX, usando navegador predeterminado: {e}")

        try:
            logger.info(f"Abriendo informe en navegador predeterminado: {file_uri}")
            webbrowser.open(file_uri)
            return True
        except Exception as e:
            logger.error(f"Error al abrir navegador: {e}")
            return False
