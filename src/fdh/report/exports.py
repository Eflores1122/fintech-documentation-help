"""CSV, a minimal XLSX and a text PDF. No extra packages."""

from __future__ import annotations

import csv
import io
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from fdh.models import AuditReport

COLUMNS = (
    "rule_id",
    "status",
    "severity",
    "area",
    "domain",
    "title",
    "condition",
    "criterion",
    "cause",
    "effect",
    "recommendation",
    "evidence",
    "document",
    "suggested_owner",
    "suggested_deadline",
    "source_name",
    "source_url",
    "verified",
    "unverified",
    "source",
    "confidence",
    "binding",
)


def _rows(report: AuditReport) -> list[list[str]]:
    table = []
    for finding in report.findings:
        table.append(
            [
                finding.rule_id,
                finding.status,
                finding.severity,
                finding.area,
                finding.domain,
                finding.title,
                finding.condition,
                finding.criterion,
                finding.cause,
                finding.effect,
                finding.recommendation,
                finding.evidence or "",
                finding.document or "",
                finding.suggested_owner,
                finding.suggested_deadline,
                finding.source_name,
                finding.source_url,
                "true" if finding.verified else "false",
                "true" if finding.unverified else "false",
                finding.source,
                "" if finding.confidence is None else f"{finding.confidence:.2f}",
                "true" if finding.binding else "false",
            ]
        )
    return table


def render_csv(report: AuditReport) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(COLUMNS)
    writer.writerows(_rows(report))
    return buffer.getvalue()


def write_xlsx(report: AuditReport, path: Path) -> None:
    _xml_row.counter = 1  # type: ignore[attr-defined]
    rows = [_xml_row(list(COLUMNS))]
    for values in _rows(report):
        rows.append(_xml_row(values))
    sheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        "<sheetData>" + "".join(rows) + "</sheetData></worksheet>"
    )
    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""
    workbook = """<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets><sheet name="Hallazgos" sheetId="1" r:id="rId1"/></sheets></workbook>"""
    wb_rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>"""
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels", wb_rels)
        archive.writestr("xl/worksheets/sheet1.xml", sheet)


def _xml_row(values: list[str]) -> str:
    row_number = _xml_row.counter  # type: ignore[attr-defined]
    _xml_row.counter = row_number + 1  # type: ignore[attr-defined]
    fixed = []
    for index, value in enumerate(values):
        ref = f"{_col(index)}{row_number}"
        fixed.append(f'<c r="{ref}" t="inlineStr"><is><t>{escape(value)}</t></is></c>')
    return f'<row r="{row_number}">' + "".join(fixed) + "</row>"


def _col(index: int) -> str:
    letters = ""
    number = index + 1
    while number:
        number, rem = divmod(number - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


_xml_row.counter = 1  # type: ignore[attr-defined]


def write_pdf(report: AuditReport, path: Path) -> None:
    lines = [
        "fintech-documentation-help",
        report.disclaimer,
        report.disclaimer_en,
        f"Entidad {report.entity_type}  catalogo {report.catalog_year}  estrictez {report.strictness}",
        f"Dictamen: {report.opinion.get('label', '')}",
        str(report.opinion.get("narrative", "")),
        f"Puntaje: {report.scores.overall}",
    ]
    for area, score in report.scores.by_area.items():
        shown = "n/a" if score is None else f"{score:.1f}"
        lines.append(f"Area {area}: {shown}")
    lines.append("Hallazgos:")
    for finding in report.findings:
        if finding.status not in {"fail", "unclear"}:
            continue
        flag = "" if finding.verified else " UNVERIFIED"
        lines.append(f"{finding.status} {finding.severity}{flag} {finding.rule_id} {finding.title}")
        lines.append(f"  Condicion: {_cut(finding.condition)}")
        lines.append(f"  Recomendacion: {_cut(finding.recommendation)}")
        lines.append(f"  Fuente: {_cut(finding.source_name)}")
    lines.append(report.disclaimer)
    _pdf_lines(path, [_latin(line) for line in lines])


def _cut(value: str) -> str:
    compact = " ".join(value.split())
    return compact[:180]


def _latin(value: str) -> str:
    return value.encode("latin-1", errors="replace").decode("latin-1")


def _pdf_lines(path: Path, lines: list[str]) -> None:
    pages: list[list[str]] = []
    size = 42
    for offset in range(0, len(lines), size):
        pages.append(lines[offset : offset + size])
    if not pages:
        pages = [[""]]
    objects: list[bytes] = []

    def add(data: str) -> int:
        objects.append(data.encode("latin-1", errors="replace"))
        return len(objects)

    font_id = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    page_ids: list[int] = []
    content_ids: list[int] = []
    for chunk in pages:
        commands = ["BT", "/F1 9 Tf", "40 800 Td", "12 TL"]
        for line in chunk:
            commands.append(f"({_pdf_escape(line)}) Tj")
            commands.append("T*")
        commands.append("ET")
        stream = "\n".join(commands)
        content_ids.append(
            add(
                f"<< /Length {len(stream.encode('latin-1', errors='replace'))} >>\nstream\n{stream}\nendstream"
            )
        )
    for content_id in content_ids:
        page_ids.append(
            add(
                "<< /Type /Page /Parent PAGES /MediaBox [0 0 612 842] "
                f"/Contents {content_id} 0 R /Resources << /Font << /F1 {font_id} 0 R >> >> >>"
            )
        )
    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    pages_id = add(f"<< /Type /Pages /Count {len(page_ids)} /Kids [{kids}] >>")
    # Parent must point at the pages object. Rewrite page objects now that the id is known.
    for page_id in page_ids:
        objects[page_id - 1] = objects[page_id - 1].replace(
            b"/Parent PAGES", f"/Parent {pages_id} 0 R".encode()
        )
    catalog_id = add(f"<< /Type /Catalog /Pages {pages_id} 0 R >>")
    blob = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(blob))
        blob.extend(f"{index} 0 obj\n".encode())
        blob.extend(obj)
        blob.extend(b"\nendobj\n")
    xref = len(blob)
    blob.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    blob.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        blob.extend(f"{offset:010d} 00000 n \n".encode())
    blob.extend(
        f"trailer << /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    )
    path.write_bytes(blob)


def _pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
