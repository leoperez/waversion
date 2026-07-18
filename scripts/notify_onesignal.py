#!/usr/bin/env python3
"""Envía una notificación push (OneSignal) avisando de una nueva versión de WhatsApp.

Se ejecuta desde el workflow SOLO cuando el scraper detecta una versión nueva.
Si no hay clave configurada, no hace nada (no rompe el workflow).

Uso:  python scripts/notify_onesignal.py "2.26.28.70"
Requiere el env var ONESIGNAL_REST_API_KEY (secret de GitHub).
"""
import json
import os
import sys
import urllib.request

APP_ID = os.environ.get("ONESIGNAL_APP_ID", "5c71d9f7-03c7-4856-bff3-b0b70a54e92a")
REST_KEY = os.environ.get("ONESIGNAL_REST_API_KEY")
API_URL = "https://onesignal.com/api/v1/notifications"


def main():
    if not REST_KEY:
        print("Sin ONESIGNAL_REST_API_KEY: no se envía notificación.")
        return 0

    version = sys.argv[1].strip() if len(sys.argv) > 1 else ""

    payload = {
        "app_id": APP_ID,
        # Segmento por defecto de OneSignal con todos los usuarios suscritos.
        "included_segments": ["Subscribed Users"],
        "headings": {
            "en": "WhatsApp update available",
            "es": "Actualización de WhatsApp",
        },
        "contents": {
            "en": (f"WhatsApp {version} is available. Open the app to check and update.").strip(),
            "es": (f"WhatsApp {version} ya está disponible. Ábrela para comprobarlo y actualizar.").strip(),
        },
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Basic {REST_KEY}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"OneSignal respondió {resp.status}: {resp.read().decode('utf-8', 'ignore')}")
    except Exception as exc:  # noqa: BLE001
        # No fallamos el workflow si la notificación no sale.
        print(f"Error enviando notificación: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
