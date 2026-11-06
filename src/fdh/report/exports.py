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
    from fdh.report.pdf_pro import write_professional_pdf

    write_professional_pdf(report, path)
    return
