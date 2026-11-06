"""Audit PDF with ReportLab. DejaVu keeps Spanish accents. No paid font."""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.colors import Color, white
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus import (
    Paragraph as RlParagraph,
)

from fdh.areas import area_label
from fdh.models import AuditReport

INK = Color(0.10, 0.11, 0.11)
RULE = Color(0.78, 0.76, 0.73)
ACCENT = Color(0.55, 0.18, 0.18)


def _p(text: object, style: ParagraphStyle) -> RlParagraph:
    return RlParagraph(escape(str(text)), style)


_FONT_CANDIDATES = (
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
)


def _font() -> str:
    for path in _FONT_CANDIDATES:
        if path.is_file():
            pdfmetrics.registerFont(TTFont("FdhBody", str(path)))
            return "FdhBody"
    return "Times-Roman"


def write_professional_pdf(report: AuditReport, path: Path) -> None:
    font = _font()
    styles = _styles(font)
    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=f"Auditoría {report.entity_type} {report.catalog_year}",
    )
    story = []
    story.append(_p("fintech-documentation-help", styles["kicker"]))
    story.append(Spacer(1, 8))
    story.append(_p(f"Auditoría documental {report.entity_type}", styles["cover"]))
    story.append(Spacer(1, 6))
    story.append(
        _p(
            f"Catálogo {report.catalog_year}"
            + (f" · a la fecha {report.as_of}" if report.as_of else " · snapshot del año"),
            styles["sub"],
        )
    )
    story.append(Spacer(1, 10))
    story.append(_p(report.disclaimer, styles["body"]))
    story.append(Spacer(1, 8))
    overall = "n/a" if report.scores.overall is None else f"{report.scores.overall:.1f}"
    story.append(_p(f"Calificación global {overall} / 100", styles["score"]))
    story.append(_p(f"Dictamen documental: {report.opinion.get('label', '')}", styles["sub"]))
    story.append(_p(str(report.opinion.get("narrative", "")), styles["body"]))
    story.append(_p(str(report.opinion.get("disclaimer", "")), styles["body"]))
    story.append(Spacer(1, 8))
    story.append(_p("Calificación por área", styles["h"]))
    story.append(_area_table(report, font))
    story.append(PageBreak())
    story.append(_p("Resumen ejecutivo", styles["h"]))
    summary = report.summary
    story.append(
        _p(
            f"Incumplimientos {summary.get('fail', 0)}, de ellos críticos "
            f"{summary.get('fail_critical', 0)} y altos {summary.get('fail_high', 0)}. "
            f"Cumple {summary.get('pass', 0)}. No aplica {summary.get('not_applicable', 0)}. "
            f"Reglas UNVERIFIED visibles: {summary.get('unverified', 0)}.",
            styles["body"],
        )
    )
    if report.parameter_gaps:
        story.append(_p("Parámetros sin valor para esta fecha", styles["h"]))
        for gap in report.parameter_gaps:
            story.append(_p(str(gap.get("message", "")), styles["body"]))
    if report.business_profile:
        story.append(_p("Perfil de negocio inferido", styles["h"]))
        profile = report.business_profile
        raw_products = profile.get("products") or []
        product_rows = raw_products if isinstance(raw_products, list) else []
        names = (
            ", ".join(str(item.get("label")) for item in product_rows if isinstance(item, dict))
            or "sin producto identificado"
        )
        story.append(
            _p(
                f"Entidad declarada {profile.get('declared_entity')}. "
                f"Sugerencia documental: {profile.get('suggested_entity')}. Productos: {names}.",
                styles["body"],
            )
        )
        for row in report.coherence:
            story.append(_p(str(row.get("message", "")), styles["body"]))
    story.append(_p("Hallazgos", styles["h"]))
    shown = 0
    for finding in report.findings:
        if finding.status not in {"fail", "unclear"}:
            continue
        flag = "" if finding.verified else " UNVERIFIED"
        story.append(
            _p(
                f"{finding.status} · {finding.severity}{flag} · {finding.rule_id}",
                styles["finding"],
            )
        )
        story.append(_p(finding.title, styles["sub"]))
        story.append(_p(finding.condition or finding.message, styles["body"]))
        story.append(
            _p(
                f"Recomendación: {finding.recommendation or finding.fix_suggestion} "
                f"Responsable: {finding.suggested_owner}. Plazo: {finding.suggested_deadline}. "
                f"Fuente: {finding.source_name}.",
                styles["body"],
            )
        )
        shown += 1
        if shown >= 40:
            story.append(
                _p(
                    "El PDF muestra 40 incumplimientos. El JSON y el Markdown traen el resto.",
                    styles["body"],
                )
            )
            break
    story.append(PageBreak())
    story.append(_p("Plan de remediación", styles["h"]))
    for item in report.remediation[:25]:
        story.append(
            _p(
                f"{item.get('rule_id')} · {item.get('severity')} · {item.get('owner')} · "
                f"{item.get('deadline')} · {item.get('status')}",
                styles["body"],
            )
        )
    story.append(_p("Anexo. Fuentes y vigencia", styles["h"]))
    story.append(
        _p(
            "Cada hallazgo conserva la URL oficial. Una ficha UNVERIFIED no cierra el número de artículo.",
            styles["body"],
        )
    )
    story.append(_p(report.disclaimer, styles["body"]))

    def _footer(canvas, _doc) -> None:
        canvas.saveState()
        canvas.setFillColor(INK)
        canvas.setFont(font, 8)
        canvas.drawString(18 * mm, 10 * mm, "No es asesoría legal ni fiscal.")
        canvas.drawRightString(letter[0] - 18 * mm, 10 * mm, str(canvas.getPageNumber()))
        canvas.restoreState()

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)


def _area_table(report: AuditReport, font: str) -> Table:
    rows = [["Área", "Puntaje"]]
    for area, score in report.scores.by_area.items():
        shown = "n/a" if score is None else f"{score:.1f}"
        rows.append([area_label(area), shown])
    if len(rows) == 1:
        rows.append(["Sin áreas ponderadas", "n/a"])
    table = Table(rows, colWidths=[120 * mm, 30 * mm])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), font),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("LINEBELOW", (0, 1), (-1, -1), 0.2, RULE),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def _styles(font: str) -> dict[str, ParagraphStyle]:
    return {
        "kicker": ParagraphStyle("kicker", fontName=font, fontSize=9, textColor=ACCENT),
        "cover": ParagraphStyle("cover", fontName=font, fontSize=22, leading=26, textColor=INK),
        "score": ParagraphStyle("score", fontName=font, fontSize=16, leading=20, textColor=INK),
        "h": ParagraphStyle(
            "h", fontName=font, fontSize=13, leading=16, textColor=INK, spaceBefore=10
        ),
        "sub": ParagraphStyle("sub", fontName=font, fontSize=11, leading=14, textColor=INK),
        "finding": ParagraphStyle(
            "finding", fontName=font, fontSize=9, leading=12, textColor=ACCENT, spaceBefore=8
        ),
        "body": ParagraphStyle(
            "body",
            fontName=font,
            fontSize=9,
            leading=12,
            textColor=INK,
            alignment=TA_JUSTIFY,
            spaceAfter=4,
        ),
    }
