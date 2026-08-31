import re
from core.logger import logger

HIGH_PRIORITY_KEYWORDS = [
    "oferta de trabajo", "entrevista", "recruiting", "empleo", "candidatura",
    "factura", "pago", "cobro", "renovacion", "renovación", "verificacion",
    "verificación", "seguridad", "acceso nuevo", "problema con cuenta", "envio",
    "envío", "pedido", "paquete", "entrega", "en reparto", "devolucion",
    "devolución", "incidencia", "banco", "tarjeta", "security alert", "alert"
]

EXCLUDE_KEYWORDS = [
    "descuento", "oferta limitada", "campaña", "marketing", "newsletter",
    "sorteo", "cupon", "cupón", "publicidad", "black friday", "rebajas",
    "promocional", "unsubscribe", "darse de baja"
]

CATEGORY_PATTERNS = {
    "Trabajo": ["trabajo", "empleo", "recruiting", "entrevista", "candidatura", "linkedin", "job"],
    "Compra / Entrega": ["pedido", "paquete", "entrega", "reparto", "amazon", "envio", "envío", "seguimiento", "dhl", "seur", "correos"],
    "Finanzas": ["factura", "pago", "cobro", "banco", "paypal", "reembolso", "tarjeta", "recibo", "transferencia"],
    "Seguridad": ["seguridad", "alerta", "security", "contraseña", "password", "verificacion", "verificación", "2fa", "access"],
    "Cuenta / Servicio": ["github", "google", "microsoft", "suscripcion", "suscripción", "servicio", "cuenta", "aviso", "soporte"]
}

class EmailPrioritizerService:
    """
    Servicio de clasificación y priorización inteligente de correo electrónico.
    Combina reglas locales rápidas y filtrado heurístico.
    """
    def prioritize_emails(self, messages, max_items=10):
        """
        Filtra y clasifica una lista de mensajes recibidos de GmailClient.
        Excluye publicidad irrelevante y destaca los correos prioritarios.
        """
        if not messages:
            return []

        prioritized = []

        for msg in messages:
            subject = msg.get("subject", "")
            snippet = msg.get("snippet", "")
            sender = msg.get("sender_name", "") + " " + msg.get("sender_email", "")

            full_text = f"{subject} {snippet} {sender}".lower()

            # Comprobar si se debe descartar por promociones/spam masivo
            if self._should_exclude(full_text):
                continue

            category = self._categorize(full_text)
            priority = self._determine_priority(full_text)

            priority_label = "Alta prioridad" if priority == "high" else "Relevante"

            prioritized.append({
                "id": msg.get("id"),
                "subject": subject,
                "sender_name": msg.get("sender_name"),
                "sender_email": msg.get("sender_email"),
                "snippet": snippet,
                "date_display": msg.get("date_display"),
                "link": msg.get("link"),
                "category": category,
                "priority": priority,
                "priority_label": priority_label
            })

        # Ordenar por prioridad (alta prioridad primero)
        prioritized.sort(key=lambda x: 0 if x["priority"] == "high" else 1)

        return prioritized[:max_items]

    def _should_exclude(self, text):
        """Determina si un correo es probablemente publicidad o newsletter masiva sin valor."""
        has_exclude_kw = any(kw in text for kw in EXCLUDE_KEYWORDS)
        has_high_priority_kw = any(kw in text for kw in HIGH_PRIORITY_KEYWORDS)

        # Si contiene palabras de exclusión y NINGUNA de alta prioridad, descartar
        if has_exclude_kw and not has_high_priority_kw:
            return True
        return False

    def _categorize(self, text):
        """Asigna la categoría principal basada en reglas de palabras clave."""
        for cat, keywords in CATEGORY_PATTERNS.items():
            if any(kw in text for kw in keywords):
                return cat
        return "Relevante"

    def _determine_priority(self, text):
        """Determina el nivel de prioridad ('high' o 'relevant')."""
        if any(kw in text for kw in HIGH_PRIORITY_KEYWORDS):
            return "high"
        return "relevant"
