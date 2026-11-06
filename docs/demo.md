# Demo sin costo

La demo de GitHub Pages corre en el navegador. No hay servidor de documentos y no hay API de pago.

URL prevista: https://eflores1122.github.io/fintech-documentation-help/

Si el sitio aún no responde, en el repositorio: Settings, Pages, Build and deployment, Source = GitHub Actions. Después hay que volver a lanzar el workflow `Pages`. El workflow pide el entorno `github-pages`, que GitHub crea al activar Pages con Actions.

## Qué corre en el navegador

- El evaluador de `site/app.js`, alimentado por `site/data/catalog.json` (el YAML del repo, exportado por `scripts/build_site.py`).
- La carga de los samples Nube Pago y Ladrillo Común.
- El perfil de negocio, la calificación por área, los hallazgos y el diagrama en texto Mermaid.
- La descarga de HTML y de un PDF de texto.
- El OCR de una imagen con Tesseract.js, que el navegador descarga de jsDelivr solo si se pulsa el botón del aviso escaneado. La imagen no se envía a un servidor nuestro.

## Qué corre solo en local

- `fdh audit`, el PDF con ReportLab, Tesseract del sistema (`tesseract-ocr-spa`) y `fdh serve`.
- La IA: `FDH_LLM_PROVIDER=ollama` (o llama.cpp, LM Studio, vLLM). Costo cero si el modelo está en la máquina.

Para que la demo hable con un Ollama del visitante, ese Ollama tiene que aceptar el origen de la página:

```bash
OLLAMA_ORIGINS=https://eflores1122.github.io ollama serve
```

La demo no llama al modelo por defecto. WebLLM no va embebido: el peso del modelo rompería la página y la revisión ya termina sin él.

## Hugging Face Space

Opcional, también gratuito. El `Dockerfile` de este repo sirve `fdh serve`. En un Space Docker se publica ese contenedor y se abre el puerto 8000. Ahí sí hay un servidor, así que no suba expedientes reales. La demo de Pages sigue siendo la vía en la que el archivo no sale del navegador.
