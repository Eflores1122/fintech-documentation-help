"""OCR for scans and photos. Tesseract is local and free. No cloud OCR."""

from __future__ import annotations

import shutil
from pathlib import Path


def tesseract_available() -> bool:
    return shutil.which("tesseract") is not None


def ocr_image(path: Path, lang: str = "spa+eng") -> tuple[str, list[str]]:
    warnings: list[str] = []
    if not tesseract_available():
        return "", [
            "Tesseract no está instalado. El OCR local no corrió. "
            "Instale tesseract-ocr y tesseract-ocr-spa. No se envió la imagen a un servicio."
        ]
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return "", ["Faltan pillow o pytesseract en el entorno local."]
    try:
        image = Image.open(path)
    except Exception as exc:
        return "", [f"No se pudo abrir la imagen: {exc}"]
    try:
        text = pytesseract.image_to_string(image, lang=lang)
    except pytesseract.TesseractError:
        text = pytesseract.image_to_string(image, lang="eng")
        warnings.append("El paquete de idioma spa no respondió. Se usó eng.")
    return text or "", warnings


def ocr_pdf_images(path: Path) -> tuple[str, list[str]]:
    """OCR embedded images when the PDF has no text layer."""
    warnings: list[str] = []
    if not tesseract_available():
        return "", ["PDF sin capa de texto y sin Tesseract local. No se usó un OCR de pago."]
    try:
        import pytesseract
        from PIL import Image
        from pypdf import PdfReader
    except ImportError:
        return "", ["Faltan pillow, pytesseract o pypdf."]
    reader = PdfReader(str(path))
    chunks: list[str] = []
    for page in reader.pages:
        images = list(getattr(page, "images", []) or [])
        if not images:
            continue
        for image in images:
            data = getattr(image, "data", None)
            if not data:
                continue
            tmp = path.with_suffix(".ocr-tmp")
            tmp.write_bytes(data)
            try:
                with Image.open(tmp) as picture:
                    chunks.append(pytesseract.image_to_string(picture, lang="spa+eng"))
            except Exception as exc:
                warnings.append(f"Una imagen del PDF no se leyó: {exc}")
            finally:
                tmp.unlink(missing_ok=True)
    if not chunks:
        warnings.append("El PDF no trae capa de texto ni una imagen que pypdf haya podido extraer.")
    return "\n".join(chunks), warnings
