"""Mermaid diagrams and a small SVG fallback. No network and no mermaid-cli required."""

from __future__ import annotations

import html
import shutil
from pathlib import Path

DIAGRAMS: dict[str, str] = {
    "mapa-areas": """flowchart LR
  legal[Legal y corporativo]
  regulatorio[CNBV y Banxico]
  financiero[Financiero]
  fiscal[Fiscal SAT]
  pld[PLD/FT]
  ciber[Ciberseguridad]
  privacidad[Datos personales]
  condusef[CONDUSEF]
  riesgos[Riesgos]
  operacion[Operación y TI]
  laboral[Laboral]
  legal --> regulatorio
  regulatorio --> financiero
  regulatorio --> pld
  regulatorio --> ciber
  financiero --> fiscal
  pld --> riesgos
  ciber --> riesgos
  privacidad --> ciber
  condusef --> operacion
  riesgos --> operacion
  laboral --> legal""",
    "flujo-auditoria": """flowchart TD
  plan[Planeación por tipo de entidad]
  inv[Inventario esperado contra presentado]
  doc[Revisión documental determinística]
  ctrl[Pruebas de controles y cédula]
  hall[Hallazgos formales]
  rem[Plan de remediación]
  seg[Seguimiento contra la auditoría anterior]
  dic[Dictamen por área y global]
  plan --> inv --> doc --> ctrl --> hall --> rem --> seg --> dic""",
    "flujo-pld": """flowchart TD
  alta[Alta de cliente]
  kyc[KYC y KYB]
  bc[Beneficiario controlador]
  list[Listas de personas bloqueadas]
  mon[Monitoreo y alertas]
  rep[Reportes relevante, inusual o interno preocupante]
  comite[Comité de comunicación y control]
  alta --> kyc --> bc --> list --> mon --> rep --> comite""",
    "flujo-incidentes": """flowchart TD
  det[Detección]
  cont[Contención]
  avisocnbv[Aviso a la CNBV: el art. 67 de IFC dice de forma inmediata]
  cinco[Información adicional: cinco días hábiles en el art. 67 de IFC]
  cliente[Aviso al cliente: 48 horas si hay información sensible, art. 67 IFC]
  plan[Plan de mitigación: quince días hábiles tras concluir, art. 67 IFC]
  det --> cont --> avisocnbv --> cinco
  cont --> cliente
  cinco --> plan""",
    "flujo-quejas": """flowchart TD
  rec[Recepción en UNE]
  folio[Folio]
  resp[Respuesta según el procedimiento]
  reca[Contrato ya inscrito en RECA]
  esc[Escalamiento a CONDUSEF si el usuario lo pide]
  rec --> folio --> resp
  reca --> rec
  resp --> esc""",
    "gobierno": """flowchart TD
  asamblea[Asamblea]
  consejo[Consejo o administrador único]
  audit[Comité de auditoría]
  ries[Comité de riesgos]
  pld[Comité de comunicación y control PLD]
  ciso[CISO en IFC, art. 65]
  une[Titular de la UNE]
  asamblea --> consejo
  consejo --> audit
  consejo --> ries
  consejo --> pld
  consejo --> ciso
  consejo --> une""",
    "gantt-obligaciones": """gantt
  title Recordatorios del año, no días legales exactos
  dateFormat YYYY-MM-DD
  section Reportes
  Series mensuales R01           :2026-01-10, 20d
  Trimestrales R13 y R27         :2026-04-20, 10d
  section Cierre
  Capital suscrito y pagado      :2026-12-15, 10d
  RMF del ejercicio              :2026-01-15, 15d
  Auditoría PLD                  :2026-03-31, 10d
  Dictamen financiero            :2026-04-30, 10d
  Prueba de continuidad          :2026-06-30, 10d""",
    "flujo-datos": """flowchart LR
  titular[Titular]
  aviso[Aviso de privacidad art. 15]
  resp[Responsable]
  enc[Encargado]
  arco[Derechos ARCO]
  aut[Secretaría Anticorrupción y Buen Gobierno]
  titular --> aviso --> resp
  resp --> enc
  titular --> arco --> resp
  titular --> aut""",
}


def mermaid_document(selected: list[str] | None = None) -> str:
    keys = selected or list(DIAGRAMS)
    parts = [
        "# Diagramas de cumplimiento",
        "",
        "Plantillas para documentar la fintech. No son asesoría legal.",
        "",
    ]
    for key in keys:
        body = DIAGRAMS[key]
        parts.extend([f"## {key}", "", "```mermaid", body, "```", ""])
    return "\n".join(parts)


def render_svg(key: str) -> str:
    """A readable box diagram when mermaid-cli is not installed."""
    title = html.escape(key)
    lines = [line.strip() for line in DIAGRAMS[key].splitlines() if line.strip()]
    labels = []
    for line in lines:
        if line.startswith(("flowchart", "gantt", "dateFormat", "title", "section")):
            continue
        chunk = line.split("[", 1)[-1].split("]", 1)[0] if "[" in line else line
        chunk = chunk.split(":", 1)[0]
        labels.append(chunk[:48])
    rows = labels[:12] or ["sin nodos"]
    height = 70 + len(rows) * 36
    boxes = []
    for index, label in enumerate(rows):
        y = 50 + index * 36
        boxes.append(
            f'<rect x="40" y="{y}" width="640" height="28" rx="4" fill="#102033"/>'
            f'<text x="52" y="{y + 18}" fill="#ffffff" font-size="13" '
            f'font-family="sans-serif">{html.escape(label)}</text>'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="{height}" '
        f'role="img" aria-label="{title}">'
        f'<rect width="100%" height="100%" fill="#f4f6f8"/>'
        f'<text x="40" y="28" font-family="sans-serif" font-size="16" fill="#102033">{title}</text>'
        + "".join(boxes)
        + "</svg>"
    )


def write_diagrams(out_dir: Path, selected: list[str] | None = None) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    keys = selected or list(DIAGRAMS)
    written = [out_dir / "diagramas.md"]
    written[0].write_text(mermaid_document(keys), encoding="utf-8")
    html_parts = [
        "<!DOCTYPE html><html lang='es'><meta charset='utf-8'/>",
        "<title>Diagramas fdh</title>",
        "<body><p>Plantillas. No son asesoría legal ni fiscal.</p>",
    ]
    for key in keys:
        svg = out_dir / f"{key}.svg"
        svg.write_text(render_svg(key), encoding="utf-8")
        written.append(svg)
        html_parts.append(f"<h2>{html.escape(key)}</h2>")
        html_parts.append(render_svg(key))
        html_parts.append("<pre class='mermaid'>")
        html_parts.append(html.escape(DIAGRAMS[key]))
        html_parts.append("</pre>")
    png = shutil.which("mmdc")
    note = (
        "Mermaid CLI está en el PATH; el SVG ya quedó escrito y el bloque mermaid también."
        if png
        else "Mermaid CLI no está instalado. Queda el SVG y el bloque mermaid."
    )
    html_parts.append(f"<p>{html.escape(note)}</p></body></html>")
    page = out_dir / "diagramas.html"
    page.write_text("\n".join(html_parts), encoding="utf-8")
    written.append(page)
    return written
