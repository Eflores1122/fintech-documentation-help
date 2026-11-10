"""Markdown, HTML and JSON reports. Every format carries the disclaimer."""

from __future__ import annotations

import html
from pathlib import Path

from fdh.models import AuditReport, Finding

DOMAIN_LABELS = {
    "privacy": "Datos personales (LFPDPPP)",
    "lritf": "LRITF",
    "banxico": "Banxico / IFPE",
    "cnbv": "CNBV",
    "pld": "PLD/FT",
    "condusef": "CONDUSEF",
    "sat": "SAT / fiscal",
    "meta": "Meta",
    "legal": "Legal y corporativo",
    "regulatorio": "Regulatorio CNBV/Banxico",
    "financiero": "Financiero y contable",
    "fiscal": "Fiscal",
    "ciberseguridad": "Ciberseguridad",
    "privacidad": "Privacidad",
    "riesgos": "Riesgos",
    "operacion": "Operación y TI",
    "laboral": "Laboral",
    "metodologia": "Modo estricto",
}

STATUS_LABELS = {
    "pass": "Cumple",
    "fail": "Incumplimiento",
    "not_applicable": "No aplica",
    "unclear": "No concluyente",
}


def render_json(report: AuditReport) -> str:
    return report.model_dump_json(indent=2) + "\n"


def render_markdown(report: AuditReport) -> str:
    lines = [
        f"# Auditoría documental {report.catalog_year} — {report.entity_type}",
        "",
        f"> **{report.disclaimer}**",
        ">",
        f"> {report.disclaimer_en}",
        "",
        f"- Herramienta: {report.tool} {report.version}",
        f"- Generado (UTC): {report.generated_at.isoformat()}",
        f"- Entidad: `{report.entity_type}` · catálogo {report.catalog_year}",
        f"- LLM: {'sí' if report.llm_used else 'no'}"
        + (f" — {report.llm_note}" if report.llm_note else ""),
        f"- Estrictez: `{report.strictness}`",
        f"- Dictamen documental: **{report.opinion.get('label', '')}**. {report.opinion.get('narrative', '')}",
        "",
        str(report.opinion.get("disclaimer", "")),
        "",
        "## Puntaje",
        "",
        _score_line("General", report.scores.overall),
        "",
        "| Dominio | Puntaje |",
        "|---|---:|",
    ]
    for domain, value in report.scores.by_domain.items():
        label = DOMAIN_LABELS.get(domain, domain)
        shown = "n/a" if value is None else f"{value:.1f}"
        lines.append(f"| {label} | {shown} |")
    if report.scores.by_area:
        lines.extend(["", "### Por área", "", "| Área | Puntaje |", "|---|---:|"])
        for area, value in report.scores.by_area.items():
            shown = "n/a" if value is None else f"{value:.1f}"
            lines.append(f"| {area} | {shown} |")
    lines.extend(["", "## Resumen", ""])
    summary = report.summary
    lines.append(
        f"- Cumple: {summary.get('pass', 0)} · Incumplimiento: {summary.get('fail', 0)} · "
        f"No aplica: {summary.get('not_applicable', 0)} · No concluyente: {summary.get('unclear', 0)}"
    )
    lines.append(
        "- Fallas por severidad: "
        + ", ".join(
            f"{name} {summary.get(f'fail_{name}', 0)}"
            for name in ("critical", "high", "medium", "low", "info")
        )
    )
    lines.append(f"- Reglas UNVERIFIED visibles en este reporte: {summary.get('unverified', 0)}")
    lines.append(
        f"- Reglas omitidas por tipo de entidad o por ser internas: {summary.get('omitted', 0)}"
    )
    lines.extend(["", "## Documentos ingeridos", ""])
    if not report.documents:
        lines.append("No se ingirió ningún archivo.")
    for doc in report.documents:
        types = ", ".join(doc.types) if doc.types else "sin clasificar"
        lines.append(f"- `{doc.path}` → {types}")
        for warning in doc.warnings:
            lines.append(f"  - aviso: {warning}")
    lines.extend(["", "## Hallazgos", ""])
    if not report.findings:
        lines.append("Sin hallazgos.")
    for finding in report.findings:
        lines.extend(_finding_md(finding))
    if report.rejected_llm_findings:
        lines.extend(["## Hallazgos del modelo descartados", ""])
        lines.append(
            "Se descartaron porque no citan un `rule_id` del catálogo o porque la cita "
            "no es un fragmento literal del documento. La herramienta no incorpora regulación inventada."
        )
        lines.append("")
        for item in report.rejected_llm_findings:
            lines.append(f"- `{item.get('rule_id', '')}`: {item.get('reason', '')}")
        lines.append("")
    if report.omitted_rules:
        lines.extend(["## Reglas no aplicadas", ""])
        for item in report.omitted_rules:
            lines.append(f"- `{item['id']}`: {item['reason']}")
        lines.append("")
    if report.remediation:
        lines.extend(
            [
                "## Plan de remediación",
                "",
                "| Regla | Severidad | Responsable | Plazo | Estado |",
                "|---|---|---|---|---|",
            ]
        )
        for row in report.remediation[:40]:
            lines.append(
                f"| `{row['rule_id']}` | {row['severity']} | {row['owner']} | "
                f"{row['deadline']} | {row['status']} |"
            )
        if len(report.remediation) > 40:
            lines.append("")
            lines.append(
                f"Se muestran 40 de {len(report.remediation)}. El JSON trae el plan completo."
            )
        lines.append("")
    if report.comparison:
        changed = [row for row in report.comparison if row.get("changed")]
        lines.extend(
            [
                "## Seguimiento",
                "",
                f"Cambios respecto de la auditoría anterior: {len(changed)}.",
                "",
            ]
        )
    lines.append("---")
    lines.append("")
    lines.append(report.disclaimer)
    lines.append("")
    return "\n".join(lines)


def _score_line(label: str, value: float | None) -> str:
    if value is None:
        return f"**{label}:** n/a (solo reglas informativas o sin reglas ponderadas)."
    return f"**{label}:** {value:.1f} / 100"


def _finding_md(finding: Finding) -> list[str]:
    flag = " · **UNVERIFIED**" if finding.unverified else ""
    rows = [
        f"### {STATUS_LABELS[finding.status]} · {finding.severity}{flag} · `{finding.rule_id}`",
        "",
        f"**{finding.title}**",
        "",
        finding.message,
        "",
        f"- Dominio: {DOMAIN_LABELS.get(finding.domain, finding.domain)}",
        f"- Requisito: {finding.requirement}",
    ]
    if finding.document:
        rows.append(f"- Documento: `{finding.document}`")
    if finding.evidence:
        rows.append(f"- Evidencia: “{finding.evidence}”")
    if finding.condition and finding.status == "fail":
        rows.append(f"- Condición: {finding.condition}")
        rows.append(f"- Criterio: {finding.criterion}")
        rows.append(f"- Causa: {finding.cause}")
        rows.append(f"- Efecto: {finding.effect}")
        rows.append(f"- Recomendación: {finding.recommendation}")
        if finding.evidence_required:
            rows.append("- Evidencia requerida: " + "; ".join(finding.evidence_required))
        rows.append(f"- Responsable sugerido: {finding.suggested_owner}")
        rows.append(f"- Plazo sugerido: {finding.suggested_deadline}")
    rows.append(f"- Corrección sugerida: {finding.fix_suggestion}")
    rows.append(
        f"- Fuente: [{finding.source_name}]({finding.source_url}) · "
        f"vigencia {finding.effective_date.isoformat()} · "
        f"verificado {finding.last_verified.isoformat()}"
    )
    if finding.unverified_detail:
        rows.append(f"- UNVERIFIED: {finding.unverified_detail}")
    if finding.notes:
        rows.append(f"- Nota: {finding.notes}")
    rows.append(f"- Origen: {', '.join(finding.origin)}")
    rows.append("")
    return rows


def render_html(report: AuditReport) -> str:
    scores = "".join(
        "<div class='card'><div class='k'>{label}</div><div class='v'>{value}</div></div>".format(
            label=html.escape(DOMAIN_LABELS.get(domain, domain)),
            value="n/a" if value is None else f"{value:.1f}",
        )
        for domain, value in report.scores.by_domain.items()
    )
    overall = "n/a" if report.scores.overall is None else f"{report.scores.overall:.1f}"
    docs = "".join(
        "<li><code>{}</code> → {}{}</li>".format(
            html.escape(doc.path),
            html.escape(", ".join(doc.types) if doc.types else "sin clasificar"),
            "".join(f"<div class='warn'>{html.escape(warning)}</div>" for warning in doc.warnings),
        )
        for doc in report.documents
    )
    findings = "".join(_finding_html(item) for item in report.findings)
    rejected = ""
    if report.rejected_llm_findings:
        items = "".join(
            "<li><code>{}</code> {}</li>".format(
                html.escape(item.get("rule_id", "")),
                html.escape(item.get("reason", "")),
            )
            for item in report.rejected_llm_findings
        )
        rejected = (
            "<h2>Hallazgos del modelo descartados</h2>"
            "<p>No citan una regla del catálogo o la evidencia no está en el documento. "
            "No se incorporó regulación inventada.</p><ul>" + items + "</ul>"
        )
    note = html.escape(report.llm_note or "")
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Auditoría {html.escape(report.entity_type)} {report.catalog_year}</title>
<style>
:root {{ color-scheme: light; }}
body {{ font-family: "Segoe UI", system-ui, sans-serif; margin: 0; background: #f4f6f8; color: #1c2430; }}
header {{ background: #102033; color: #fff; padding: 1.25rem 1.5rem 1.5rem; }}
header h1 {{ margin: 0 0 .35rem; font-size: 1.35rem; }}
.banner {{ background: #fff4d6; color: #5c4300; border-bottom: 3px solid #e0b000; padding: 1rem 1.5rem; line-height: 1.45; }}
main {{ padding: 1.25rem 1.5rem 3rem; max-width: 980px; margin: 0 auto; }}
.cards {{ display: flex; flex-wrap: wrap; gap: .6rem; margin: .8rem 0 1.2rem; }}
.card {{ background: #fff; border-radius: 8px; padding: .7rem .85rem; min-width: 140px; box-shadow: 0 1px 2px rgba(0,0,0,.06); }}
.card .k {{ font-size: .75rem; color: #5c6b7a; }}
.card .v {{ font-size: 1.35rem; font-weight: 650; }}
.overall {{ background: #102033; color: #fff; }}
.overall .k {{ color: #c5d0dc; }}
article {{ background: #fff; border-radius: 8px; padding: .9rem 1rem; margin: .7rem 0; border-left: 5px solid #8aa; }}
article.fail {{ border-color: #b42318; }}
article.pass {{ border-color: #067647; }}
article.not_applicable {{ border-color: #98a2b3; }}
article.unclear {{ border-color: #b54708; }}
.meta {{ color: #475467; font-size: .92rem; }}
.badge {{ display: inline-block; font-size: .72rem; font-weight: 700; letter-spacing: .03em; padding: .1rem .4rem; border-radius: 4px; background: #f2f4f7; }}
.badge.critical {{ background: #fecdca; color: #7a271a; }}
.badge.high {{ background: #f9dbaf; color: #7a2e0e; }}
.badge.unverified {{ background: #fef0c7; color: #7a5b00; }}
blockquote {{ margin: .4rem 0; padding: .4rem .7rem; background: #f8fafc; border-left: 3px solid #d0d5dd; }}
a {{ color: #175cd3; }}
code {{ font-size: .92em; }}
.footer {{ margin-top: 2rem; font-size: .92rem; color: #344054; }}
</style>
</head>
<body>
<header>
<h1>fintech-documentation-help · {html.escape(report.entity_type)} · {report.catalog_year}</h1>
<div>{html.escape(report.tool)} {html.escape(report.version)} · {html.escape(report.generated_at.isoformat())} · LLM: {"sí" if report.llm_used else "no"} {note}</div>
</header>
<div class="banner"><strong>{html.escape(report.disclaimer)}</strong><br/>{html.escape(report.disclaimer_en)}</div>
<main>
<h2>Puntaje</h2>
<div class="cards">
<div class="card overall"><div class="k">General</div><div class="v">{overall}</div></div>
{scores}
</div>
<p>Cumple {report.summary.get("pass", 0)} · Incumplimiento {report.summary.get("fail", 0)} · No aplica {report.summary.get("not_applicable", 0)} · UNVERIFIED {report.summary.get("unverified", 0)}</p>
<h2>Documentos</h2>
<ul>{docs or "<li>Sin archivos.</li>"}</ul>
<h2>Hallazgos</h2>
{findings or "<p>Sin hallazgos.</p>"}
{rejected}
<p class="footer">{html.escape(report.disclaimer)}</p>
</main>
</body>
</html>
"""


def _finding_html(finding: Finding) -> str:
    badges = (
        f"<span class='badge'>{html.escape(STATUS_LABELS[finding.status])}</span> "
        f"<span class='badge {html.escape(finding.severity)}'>{html.escape(finding.severity)}</span> "
    )
    if finding.unverified:
        badges += "<span class='badge unverified'>UNVERIFIED</span> "
    evidence = ""
    if finding.evidence:
        evidence = f"<blockquote>{html.escape(finding.evidence)}</blockquote>"
    detail = ""
    if finding.unverified_detail:
        detail = f"<p class='meta'>UNVERIFIED: {html.escape(finding.unverified_detail)}</p>"
    notes = f"<p class='meta'>{html.escape(finding.notes)}</p>" if finding.notes else ""
    document = (
        f"<p class='meta'>Documento: <code>{html.escape(finding.document)}</code></p>"
        if finding.document
        else ""
    )
    return (
        f"<article class='{html.escape(finding.status)}'>"
        f"<p>{badges}<code>{html.escape(finding.rule_id)}</code></p>"
        f"<h3>{html.escape(finding.title)}</h3>"
        f"<p>{html.escape(finding.message)}</p>"
        f"{document}{evidence}"
        f"<p><strong>Corrección sugerida.</strong> {html.escape(finding.fix_suggestion)}</p>"
        f"<p class='meta'>Requisito: {html.escape(finding.requirement)}</p>"
        f"<p class='meta'>Fuente: <a href='{html.escape(finding.source_url)}'>{html.escape(finding.source_name)}</a>"
        f" · vigencia {finding.effective_date.isoformat()} · verificado {finding.last_verified.isoformat()}</p>"
        f"{detail}{notes}"
        "</article>"
    )


def write_reports(report: AuditReport, out_dir: Path, formats: list[str]) -> list[Path]:
    from fdh.calendar_data import render_ics
    from fdh.diagrams import write_diagrams
    from fdh.report.exports import render_csv, write_pdf, write_xlsx

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    selected = {item.strip().lower() for item in formats if item.strip()}
    if "md" in selected or "markdown" in selected:
        path = out_dir / "report.md"
        path.write_text(render_markdown(report), encoding="utf-8")
        written.append(path)
    if "html" in selected:
        path = out_dir / "report.html"
        path.write_text(render_html(report), encoding="utf-8")
        written.append(path)
    if "json" in selected:
        path = out_dir / "report.json"
        path.write_text(render_json(report), encoding="utf-8")
        written.append(path)
    if "csv" in selected:
        path = out_dir / "hallazgos.csv"
        path.write_text(render_csv(report), encoding="utf-8")
        written.append(path)
    if "xlsx" in selected:
        path = out_dir / "hallazgos.xlsx"
        write_xlsx(report, path)
        written.append(path)
    if "pdf" in selected:
        path = out_dir / "report.pdf"
        write_pdf(report, path)
        written.append(path)
    if "ics" in selected:
        path = out_dir / "obligaciones.ics"
        path.write_text(render_ics(report.entity_type, report.catalog_year), encoding="utf-8")
        written.append(path)
    if "diagrams" in selected or "html" in selected:
        written.extend(write_diagrams(out_dir / "diagramas"))
    return written
