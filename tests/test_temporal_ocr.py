"""As-of selection, parameters, business profile, OCR and the ReportLab PDF."""

from datetime import date
from pathlib import Path

from fdh.business import infer_business
from fdh.diff import diff_as_of
from fdh.engine.audit import run_audit
from fdh.ingest.ocr import ocr_image
from fdh.models import Profile
from fdh.parameters import resolve_parameters
from fdh.report.pdf_pro import write_professional_pdf
from fdh.temporal import rules_as_of, snapshot_year


def test_as_of_future_reuses_latest_and_flags_missing_parameters():
    rules, notes = rules_as_of(date(2031, 3, 15))
    assert snapshot_year(date(2031, 3, 15)) == 2026
    assert rules
    assert any("2031" in note or "2026" in note for note in notes)
    ids = {rule.id for rule in rules}
    assert "sat-lif2026-ifc-retencion-isr-iva" in ids
    _values, gaps = resolve_parameters(date(2031, 3, 15), ids)
    gap_ids = {item["id"] for item in gaps}
    assert "lif_isr_retencion_intereses_residentes" in gap_ids
    assert "uma_diaria" in gap_ids
    assert "pld_umbral_operacion_relevante_uma" in gap_ids
    assert all(
        "no hay valor" in str(item["message"]).lower() or "No hay valor" in str(item["message"])
        for item in gaps
    )


def test_as_of_before_privacy_reform_drops_that_rule():
    rules, _notes = rules_as_of(date(2025, 1, 1))
    ids = {rule.id for rule in rules}
    assert "privacy-aviso-art15-elementos" not in ids
    assert snapshot_year(date(2024, 6, 1)) is None
    empty, notes = rules_as_of(date(2024, 6, 1))
    assert empty == []
    assert notes


def test_date_diff_and_business_profile(samples: Path, tmp_path: Path):
    payload = diff_as_of(date(2025, 1, 1), date(2026, 1, 1))
    assert payload["from_date"] == "2025-01-01"
    assert payload["summary"]["rules_after"] >= payload["summary"]["rules_before"]
    report = run_audit([samples], Profile(entity_type="IFPE", year=2026))
    products = {item["id"] for item in report.business_profile["products"]}
    assert "wallet" in products
    assert any(item["id"] == "coherencia-wallet-sin-segregacion" for item in report.coherence)
    assert report.parameter_gaps
    later = run_audit(
        [samples],
        Profile(entity_type="IFPE", year=2031, as_of=date(2031, 3, 15)),
    )
    assert later.as_of == "2031-03-15"
    assert any(item["id"] == "uma_diaria" for item in later.parameter_gaps)
    profile = infer_business([], "IFC", {"crowdfunding": True})
    assert profile["suggested_entity"] == "IFC"
    pdf = tmp_path / "informe.pdf"
    write_professional_pdf(report, pdf)
    assert pdf.read_bytes().startswith(b"%PDF")


def test_ocr_scanned_notice(repo: Path):
    image = repo / "samples" / "nube_pago" / "docs" / "aviso_escaneado.png"
    text, warnings = ocr_image(image)
    assert not warnings
    assert "INAI" in text
    assert "privacidad" in text.lower()
