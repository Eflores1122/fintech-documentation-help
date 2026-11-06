"""Minimal PDF writer used for synthetic samples and tests.

Helvetica text is encoded as Latin-1. The real auditor reads PDFs with pypdf;
this writer only exists so the repository can ship a text PDF without a
typesetting dependency.
"""

from __future__ import annotations

from pathlib import Path


def _escape(line: str) -> str:
    encoded = line.encode("latin-1", errors="replace").decode("latin-1")
    return encoded.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf(text: str) -> bytes:
    lines = text.splitlines() or [""]
    commands = ["BT", "/F1 11 Tf"]
    y = 760
    for line in lines:
        if y < 48:
            break
        commands.append(f"1 0 0 1 48 {y} Tm ({_escape(line)}) Tj")
        y -= 16
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1", errors="replace")
    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Count 1 /Kids [3 0 R] >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>"
        ),
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        (f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n").encode(
            "ascii"
        )
    )
    return bytes(output)


def write_simple_pdf(path: Path, text: str) -> None:
    path.write_bytes(build_pdf(text))
