#!/usr/bin/env python3
"""Actualiza whatsapp_variants.json con la última versión estable de WhatsApp.

Diseño A PRUEBA DE FALLOS: si no consigue una versión válida de ninguna fuente,
NO toca el JSON (se mantiene el último valor bueno). Nunca corrompe el fichero
ni deja la app sin datos. Esa es justo la lección del backend anterior.

Se puede ejecutar a mano en cualquier momento:  python scripts/update_version.py
"""
import json
import os
import re
import sys
import urllib.request

JSON_PATH = "whatsapp_variants.json"

# Fuentes ordenadas por fiabilidad. NO usamos APKMirror (bloquea con Cloudflare).
SOURCES = [
    "https://www.whatsapp.com/android/",
    "https://whatsapp-messenger.en.uptodown.com/android",
    "https://www.techspot.com/downloads/5748-whatsapp-for-android.html",
]

# Versiones de WhatsApp: 2.AA.BB.CC
VERSION_RE = re.compile(r"2\.\d{2}\.\d{1,2}\.\d{1,3}")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    )
}


def _key(version: str):
    return [int(x) for x in version.split(".")]


def fetch_version():
    """Devuelve la versión más alta encontrada en las fuentes, o None."""
    for url in SOURCES:
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
            matches = VERSION_RE.findall(html)
            if matches:
                best = sorted(set(matches), key=_key)[-1]
                print(f"[ok] Versión encontrada en {url}: {best}")
                return best
            print(f"[--] Sin coincidencias en {url}")
        except Exception as exc:  # noqa: BLE001 - queremos tragar cualquier fallo
            print(f"[!!] Fallo con {url}: {exc}", file=sys.stderr)
    return None


def emit_output(changed: bool, version: str):
    """Expone el resultado al workflow de GitHub Actions (para decidir si notificar)."""
    out = os.environ.get("GITHUB_OUTPUT")
    if not out:
        return
    with open(out, "a", encoding="utf-8") as fh:
        fh.write(f"changed={'true' if changed else 'false'}\n")
        fh.write(f"version={version}\n")


def main():
    version = fetch_version()
    if not version:
        print("No se obtuvo ninguna versión válida. Se mantiene el JSON actual (last-good).")
        emit_output(False, "")
        return 0

    with open(JSON_PATH, encoding="utf-8") as fh:
        data = json.load(fh)

    changed = False
    for variant in data.get("Variants", []):
        if variant.get("Version") != version:
            variant["Version"] = version
            changed = True

    if changed:
        with open(JSON_PATH, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        print(f"JSON actualizado a la versión {version}.")
    else:
        print(f"El JSON ya estaba en la última versión ({version}). Sin cambios.")

    emit_output(changed, version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
