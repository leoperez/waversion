# waversion

Backend mínimo (solo un JSON estático) que alimenta la app **AppUpdater para WhatsApp**
(`com.ines.appupdater`). Sustituye al antiguo servidor de Render (`waupdate.onrender.com`),
que se cayó y dejó la app sin funcionar.

## Cómo funciona

```
[GitHub Actions cron]  ──1x/día──►  whatsapp_variants.json  ◄──lee──  App Android
   scripts/update_version.py         (servido por GitHub Pages)
   si falla: NO toca el JSON
```

- **`whatsapp_variants.json`** — el dato que consume la app. Se puede editar a mano en cualquier momento.
- **`scripts/update_version.py`** — actualiza la versión de WhatsApp desde fuentes fiables
  (whatsapp.com / Uptodown; **nunca APKMirror**, que bloquea el scraping). Si no encuentra
  versión, deja el JSON como estaba.
- **`.github/workflows/update-version.yml`** — lanza el scraper a diario. También se puede
  ejecutar a mano en la pestaña **Actions → Run workflow**.

## Contrato del JSON (NO cambiar las claves)

La app parsea claves EXACTAS, con espacios y dos puntos incluidos. Y `version minima de Android`
debe llevar el prefijo `Android ` (8 caracteres) porque la app recorta los 8 primeros caracteres.

```json
{
  "Variants": [
    { "Version": "2.26.28.4", "arquitectura: ": "arm64-v8a", "version minima de Android: ": "Android 5.0", "screen_dpi: ": "nodpi" }
  ],
  "Whats New": [ "Título de novedades", "línea 1", "línea 2" ]
}
```

- `Whats New` debe tener **al menos 1 elemento** (el primero es el título; el resto, el cuerpo).
- Todas las variantes deberían llevar la **misma `Version`** (la actual): así la app muestra bien "última versión".

## Desplegar (una sola vez)

1. Sube este repo a GitHub (`origin` ya apunta a `github.com/leoperez/waversion`).
2. **Settings → Pages →** *Deploy from a branch* → `main` / `/ (root)` → Save.
3. En unos minutos el JSON estará en:
   ```
   https://leoperez.github.io/waversion/whatsapp_variants.json
   ```
   Esta es la URL que usa la app.

## Actualizar a mano

Edita `whatsapp_variants.json`, haz commit y push. GitHub Pages lo publica solo.
