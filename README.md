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

## Notificaciones push inmediatas (OneSignal)

Cuando el scraper detecta una **versión nueva** de WhatsApp, el workflow envía un push
a todos los usuarios vía OneSignal (la app ya lleva el SDK integrado). Llega al instante,
incluso a los usuarios con la versión antigua de la app, y los reengancha.

**Para activarlo (una sola vez):**

1. En **OneSignal** → tu app → **Settings → Keys & IDs** → copia la **REST API Key**.
2. En GitHub → repo `waversion` → **Settings → Secrets and variables → Actions → New repository secret**:
   - Name: `ONESIGNAL_REST_API_KEY`
   - Value: (la REST API Key)
3. Listo. En la próxima versión nueva de WhatsApp que detecte el cron, se enviará el push.

- Si el secret **no** está configurado, el workflow simplemente **no notifica** (no falla).
- Solo se notifica cuando la versión **cambia** de verdad (nunca se repite el mismo aviso).
- La frecuencia depende del cron (hoy: diario). Como Uptodown lista versiones estables
  (~semanales), en la práctica es ~1 aviso por versión estable. Para más inmediatez, sube
  la frecuencia del cron en `update-version.yml` (p.ej. `0 */6 * * *` = cada 6 h).
- El texto del push se edita en `scripts/notify_onesignal.py` (bloque `contents`).

## Actualizar a mano

Edita `whatsapp_variants.json`, haz commit y push. GitHub Pages lo publica solo.
