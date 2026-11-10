"""Hash official pages and report when they change. Does not invent rules."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from pathlib import Path

import httpx

from fdh.catalog import locate_rules_dir

SOURCES: tuple[tuple[str, str], ...] = (
    (
        "sat-rmf-2026",
        "https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/normatividad_rmf_rgce2026.html",
    ),
    (
        "cnbv-fintech",
        "https://www.cnbv.gob.mx/SECTORES-SUPERVISADOS/Fintech/Paginas/NORMATIVIDAD-FINTECH.aspx",
    ),
    (
        "banxico-circular-12-2018",
        "https://www.banxico.org.mx/marco-normativo/normativa-emitida-por-el-banco-de-mexico/circular-12-2018/operaciones-fondos-pago-banco.html",
    ),
    (
        "lritf-diputados",
        "https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf",
    ),
    (
        "dof-criterios-2025",
        "https://dof.gob.mx/2025/SHCP/SHCP_090925.pdf",
    ),
)


def default_fetch(url: str) -> bytes:
    response = httpx.get(url, timeout=30.0, follow_redirects=True)
    response.raise_for_status()
    return response.content


def run_watch(
    rules_dir: Path | None = None,
    lock_path: Path | None = None,
    fetch: Callable[[str], bytes] | None = None,
) -> tuple[int, str]:
    root = locate_rules_dir(rules_dir)
    lock = lock_path or (root / "source-lock.json")
    previous: dict = {}
    if lock.is_file():
        previous = json.loads(lock.read_text(encoding="utf-8"))
    getter = fetch or default_fetch
    current: dict[str, dict[str, str]] = {}
    changed: list[str] = []
    errors: list[str] = []
    first = not lock.is_file()
    for key, url in SOURCES:
        try:
            body = getter(url)
        except Exception as exc:  # network and HTTP errors stay visible, not fatal
            errors.append(f"{key}: {exc}")
            old = previous.get(key)
            if isinstance(old, dict):
                current[key] = old
            continue
        digest = hashlib.sha256(body).hexdigest()
        current[key] = {"url": url, "sha256": digest}
        old_digest = ""
        stored = previous.get(key)
        if isinstance(stored, dict):
            old_digest = str(stored.get("sha256", ""))
        if old_digest and old_digest != digest:
            changed.append(f"{key} cambió ({url})")
    lock.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "Vigilancia de fuentes oficiales. No es asesoría legal ni fiscal.",
        "Un cambio de hash no crea reglas: abre trabajo humano de lectura.",
        "",
    ]
    if first:
        lines.append(f"Candado inicial escrito en {lock}. La siguiente corrida comparará.")
    if changed:
        lines.append("Cambios:")
        lines.extend(f"- {item}" for item in changed)
    elif not first:
        lines.append("Sin cambios de hash en las fuentes que respondieron.")
    if errors:
        lines.append("Fuentes que no respondieron (no se abre hallazgo por ello):")
        lines.extend(f"- {item}" for item in errors)
    text = "\n".join(lines) + "\n"
    report = root / "watch-report.md"
    report.write_text(text, encoding="utf-8")
    if changed:
        return 3, text
    return 0, text
