import os
import sys
import json
import shutil
import tempfile
from datetime import datetime

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath('.'))

from core.config import Config
from services.memory_service import MemoryService
from integrations.google_auth import GoogleAuthManager
from integrations.google_calendar_client import GoogleCalendarClient
from integrations.gmail_client import GmailClient
from services.email_prioritizer_service import EmailPrioritizerService
from integrations.news_provider import NewsProvider
from services.news_service import NewsService
from integrations.crypto_client import CryptoClient
from services.market_service import MarketService
from services.report_html_service import ReportHTMLService
from services.daily_briefing_service import DailyBriefingService
from core.intent_router import IntentRouter, Intent

def test_memory_service_fase12():
    print("--- Testing MemoryService Daily Briefing Integration ---")
    memory = MemoryService()
    briefing_data = memory.get_daily_briefing_data()
    print("Default briefing data:", briefing_data)
    assert "last_auto_generated_date" in briefing_data
    assert "last_generated_at" in briefing_data
    
    settings = memory.get_daily_briefing_settings()
    print("Default briefing settings:", settings)
    assert settings.get("enabled") is True
    print("MemoryService Fase 12 Test PASSED!")

def test_email_prioritizer():
    print("\n--- Testing EmailPrioritizerService ---")
    prioritizer = EmailPrioritizerService()
    sample_emails = [
        {
            "id": "1",
            "subject": "Oferta de trabajo en Desarrollo Python",
            "sender_name": "Recruiter Team",
            "sender_email": "jobs@example.com",
            "snippet": "Nos gustaría invitarte a una entrevista para el puesto de Senior Python Engineer.",
            "date_display": "Hace 10 min",
            "link": "https://mail.google.com/1"
        },
        {
            "id": "2",
            "subject": "50% de descuento en zapatillas",
            "sender_name": "Tienda Moda",
            "sender_email": "promo@marketing.com",
            "snippet": "¡Oferta limitada! Cupón de descuento exclusivo para ti.",
            "date_display": "Hace 1 h",
            "link": "https://mail.google.com/2"
        },
        {
            "id": "3",
            "subject": "Tu pedido de Amazon está en reparto",
            "sender_name": "Amazon.es",
            "sender_email": "shipment@amazon.es",
            "snippet": "Entrega prevista hoy antes de las 20:00.",
            "date_display": "Hace 2 h",
            "link": "https://mail.google.com/3"
        }
    ]
    res = prioritizer.prioritize_emails(sample_emails)
    print(f"Prioritized {len(res)} emails out of {len(sample_emails)}")
    for e in res:
        print(f" - [{e['category']}] ({e['priority_label']}) {e['subject']}")
    
    assert len(res) == 2 # The discount promo should be excluded!
    assert res[0]["priority"] == "high"
    print("EmailPrioritizerService Test PASSED!")

def test_crypto_market():
    print("\n--- Testing CryptoClient & MarketService ---")
    market = MarketService()
    res = market.get_market_summary()
    print("Market summary response:", json.dumps(res, indent=2))
    assert "available" in res
    if res["available"]:
        assert "BTC" in res["data"]
        assert "ETH" in res["data"]
        print(f"BTC EUR: {res['data']['BTC']['price_eur']} | ETH EUR: {res['data']['ETH']['price_eur']}")
    print("MarketService Test PASSED!")

def test_news_service():
    print("\n--- Testing NewsProvider & NewsService ---")
    news_svc = NewsService()
    res = news_svc.get_curated_news(max_per_category=2)
    print("News summary response available:", res["available"])
    if res["available"]:
        print(f"Total curated news count: {res['total_count']}")
        for cat, list_art in res["categories"].items():
            print(f" Category '{cat}': {len(list_art)} articles")
            for a in list_art:
                print(f"   * [{a['source']}] {a['title']}")
    print("NewsService Test PASSED!")

def test_html_report_generation():
    print("\n--- Testing HTML Report Generation ---")
    html_svc = ReportHTMLService()
    
    dummy_calendar = {
        "connected": True,
        "today_events": [
            {
                "summary": "Reunión de proyecto A.L.F.A.",
                "time_str": "16:30 - 17:30",
                "time_until": "faltan 20 min",
                "location": "Google Meet",
                "is_important": True
            }
        ],
        "upcoming_events": [
            {
                "summary": "Entrega de la Fase 12",
                "date_display": "02 SEP",
                "time_until": "faltan 2 días",
                "is_important": True
            }
        ]
    }
    
    dummy_emails = {
        "connected": True,
        "messages": [
            {
                "subject": "Tu pedido está en camino",
                "sender_name": "Amazon Logistics",
                "snippet": "El paquete llegará hoy.",
                "date_display": "Hoy 14:15",
                "category": "Compra / Entrega",
                "priority": "high",
                "link": "#"
            }
        ]
    }
    
    dummy_news = {
        "available": True,
        "total_count": 2,
        "categories": {
            "IA": [
                {
                    "title": "Avances en modelos de lenguaje multimodal",
                    "summary": "Los nuevos modelos de IA demuestran capacidades mejoradas.",
                    "source": "TechCrunch AI",
                    "link": "https://example.com/ai"
                }
            ]
        }
    }
    
    dummy_crypto = {
        "available": True,
        "updated_at": "16:11",
        "source": "CoinGecko",
        "data": {
            "BTC": {"name": "Bitcoin", "symbol": "BTC", "price_eur": 58420.50, "price_usd": 63500.00, "change_24h": 2.45},
            "ETH": {"name": "Ethereum", "symbol": "ETH", "price_eur": 2450.10, "price_usd": 2660.00, "change_24h": -1.12}
        }
    }
    
    path = html_svc.generate_report(dummy_calendar, dummy_emails, dummy_news, dummy_crypto, target_date="2026-08-31")
    print("Report path generated:", path)
    assert os.path.exists(path)
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "A.L.F.A." in content
    assert "#06111F" in content
    assert "#0A1A2D" in content
    assert "#FF334D" in content
    assert "#F4C542" in content
    assert "Reunión de proyecto A.L.F.A." in content
    assert "Tu pedido está en camino" in content
    assert "Bitcoin" in content
    print("ReportHTMLService Test PASSED!")

def test_daily_briefing_rule():
    print("\n--- Testing DailyBriefingService Single-Generation-Per-Day Rule ---")
    memory = MemoryService()
    
    # Clean test state for today
    today_str = datetime.now().strftime("%Y-%m-%d")
    memory.update_daily_briefing_data({"last_auto_generated_date": ""})
    
    briefing_svc = DailyBriefingService(memory_service=memory)
    
    # 1. First run today -> Should generate
    res1 = briefing_svc.check_and_auto_generate_on_startup()
    print("First run result:", res1)
    assert res1["success"] is True
    assert res1["already_generated"] is False
    
    # 2. Second run today -> Should skip
    res2 = briefing_svc.check_and_auto_generate_on_startup()
    print("Second run result:", res2)
    assert res2["success"] is True
    assert res2["already_generated"] is True
    
    # 3. Forced manual update -> Should regenerate
    res3 = briefing_svc.generate_briefing(force=True, mode="manual_command", open_browser=False)
    print("Forced update result:", res3)
    assert res3["success"] is True
    assert res3["already_generated"] is False
    
    print("DailyBriefingService Rule Test PASSED!")

def test_intent_router_fase12():
    print("\n--- Testing IntentRouter for Daily Briefing Triggers ---")
    router = IntentRouter()
    
    intent1, payload1 = router.route("Alfa, genera mi informe diario")
    print("Trigger 'genera mi informe diario':", intent1)
    assert intent1 == Intent.GENERATE_DAILY_BRIEFING
    
    intent2, payload2 = router.route("Alfa, actualiza mi informe diario")
    print("Trigger 'actualiza mi informe diario':", intent2)
    assert intent2 == Intent.GENERATE_DAILY_BRIEFING
    
    intent3, payload3 = router.route("Alfa, abre mi informe diario")
    print("Trigger 'abre mi informe diario':", intent3)
    assert intent3 == Intent.OPEN_DAILY_BRIEFING
    
    intent4, payload4 = router.route("Alfa, dame el resumen de hoy")
    print("Trigger 'dame el resumen de hoy':", intent4)
    assert intent4 == Intent.GENERATE_DAILY_BRIEFING
    
    intent5, payload5 = router.route("Alfa, estado del informe diario")
    print("Trigger 'estado del informe diario':", intent5)
    assert intent5 == Intent.STATUS_DAILY_BRIEFING
    
    intent6, payload6 = router.route("Alfa, conecta Gmail")
    print("Trigger 'conecta Gmail':", intent6)
    assert intent6 == Intent.CONFIG_GOOGLE

    print("IntentRouter Fase 12 Test PASSED!")

if __name__ == "__main__":
    test_memory_service_fase12()
    test_email_prioritizer()
    test_crypto_market()
    test_news_service()
    test_html_report_generation()
    test_daily_briefing_rule()
    test_intent_router_fase12()
    print("\n==========================================")
    print("ALL FASE 12 FUNCTIONAL TESTS PASSED SUCCESSFULLY!")
    print("==========================================")
