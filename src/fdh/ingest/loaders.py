"""Load PDF, DOCX, Markdown, TXT and HTML into plain text."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

from fdh.ingest.classify import classify_heuristic, classify_with_llm, vocabulary
from fdh.models import Document
from fdh.textutil import normalize_text

SUPPORTED = {".txt", ".md", ".markdown", ".pdf", ".docx", ".html", ".htm"}
MAX_BYTES = 20 * 1024 * 1024
_TAG_SPACE = re.compile(r"\s+")


class _HTMLText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self._skip = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"}:
            self._skip = False

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self.parts.append(data)


def html_to_text(raw: str) -> str:
    parser = _HTMLText()
    parser.feed(raw)
    return _TAG_SPACE.sub(" ", " ".join(parser.parts)).strip()


def load_documents(
    paths: list[Path],
    llm_complete=None,
    extra_types: set[str] | None = None,
) -> list[Document]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(item for item in sorted(path.rglob("*")) if item.is_file())
        elif path.is_file():
            files.append(path)
    root = _common_root(files) if files else None
    allowed = set(vocabulary())
    if extra_types:
        allowed |= extra_types
    documents: list[Document] = []
    for file in files:
        if file.name.startswith("."):
            continue
        documents.append(_load_one(file, root, llm_complete, allowed))
    return documents


def _common_root(files: list[Path]) -> Path:
    if len(files) == 1:
        return files[0].parent
    return _shared(files)


def _shared(files: list[Path]) -> Path:
    parts = [file.resolve().parent.parts for file in files]
    common: list[str] = []
    for pieces in zip(*parts, strict=False):
        if len(set(pieces)) != 1:
            break
        common.append(pieces[0])
    return Path(*common) if common else files[0].parent


def _relative(file: Path, root: Path | None) -> str:
    if root is None:
        return file.name
    try:
        return str(file.resolve().relative_to(root))
    except ValueError:
        return file.name


def _load_one(file: Path, root: Path | None, llm_complete, allowed: set[str]) -> Document:
    suffix = file.suffix.lower()
    rel = _relative(file, root)
    warnings: list[str] = []
    if suffix not in SUPPORTED:
        return Document(
            path=rel,
            filename=file.name,
            media_type=suffix or "unknown",
            text="",
            warnings=[f"Extensión no soportada ({suffix or 'sin extensión'}); se omitió el texto."],
        )
    try:
        size = file.stat().st_size
    except OSError as exc:
        return Document(
            path=rel,
            filename=file.name,
            media_type=suffix,
            text="",
            warnings=[f"No se pudo leer el archivo: {exc}"],
        )
    if size > MAX_BYTES:
        return Document(
            path=rel,
            filename=file.name,
            media_type=suffix,
            text="",
            warnings=[f"Archivo mayor a {MAX_BYTES // (1024 * 1024)} MB; se omitió."],
        )
    try:
        text = _extract(file, suffix)
    except Exception as exc:  # extraction libraries raise many types
        return Document(
            path=rel,
            filename=file.name,
            media_type=suffix.lstrip("."),
            text="",
            warnings=[f"No se pudo extraer texto: {exc}"],
        )
    text = normalize_text(text)
    if not text:
        warnings.append("El archivo no contiene texto extraíble.")
    types = classify_heuristic(file.name, text, allowed)
    if llm_complete is not None and text:
        for label in classify_with_llm(file.name, text, llm_complete, allowed):
            if label not in types:
                types.append(label)
    return Document(
        path=rel,
        filename=file.name,
        media_type=suffix.lstrip("."),
        text=text,
        types=types,
        warnings=warnings,
    )


def _extract(file: Path, suffix: str) -> str:
    if suffix in {".txt", ".md", ".markdown"}:
        return _read_text(file)
    if suffix in {".html", ".htm"}:
        return html_to_text(_read_text(file))
    if suffix == ".docx":
        return _docx(file)
    if suffix == ".pdf":
        return _pdf(file)
    raise ValueError(f"Extensión no soportada: {suffix}")


def _read_text(file: Path) -> str:
    data = file.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1", errors="replace")


def _docx(file: Path) -> str:
    import docx

    document = docx.Document(str(file))
    chunks = [paragraph.text for paragraph in document.paragraphs]
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                chunks.append(" | ".join(cells))
    return "\n".join(chunks)


def _pdf(file: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(file))
    pages = [(page.extract_text() or "") for page in reader.pages]
    return "\n".join(pages)
