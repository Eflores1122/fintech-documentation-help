"""Small local UI: upload documents and read the HTML report.

Nothing is sent to a third-party model unless the operator checks the LLM box
and the process has FDH_LLM_API_KEY. The default path is fully local.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

from fdh import __version__
from fdh.catalog import CatalogError
from fdh.disclaimer import DISCLAIMER_EN, DISCLAIMER_ES
from fdh.engine.audit import run_audit
from fdh.models import Profile, canonical_entity
from fdh.report.render import render_html, render_json

app = FastAPI(
    title="fintech-documentation-help",
    version=__version__,
    description=DISCLAIMER_ES,
)

_FORM = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>fintech-documentation-help</title>
<style>
body {{ font-family: "Segoe UI", system-ui, sans-serif; margin: 0; background: #f4f6f8; color: #1c2430; }}
.banner {{ background: #fff4d6; border-bottom: 3px solid #e0b000; padding: 1rem 1.25rem; }}
main {{ max-width: 720px; margin: 1.5rem auto; background: #fff; padding: 1.25rem 1.4rem 1.6rem; border-radius: 10px; }}
label {{ display: block; margin: .8rem 0 .25rem; font-weight: 600; }}
input, select {{ font: inherit; padding: .4rem .5rem; }}
button {{ margin-top: 1rem; background: #102033; color: #fff; border: 0; padding: .6rem 1rem; border-radius: 6px; font: inherit; cursor: pointer; }}
.hint {{ color: #475467; font-size: .92rem; }}
</style>
</head>
<body>
<div class="banner"><strong>{DISCLAIMER_ES}</strong><br/>{DISCLAIMER_EN}</div>
<main>
<h1>Auditor documental</h1>
<p class="hint">Suba políticas, contratos, avisos o manuales (PDF, DOCX, Markdown, TXT, HTML). Entidad de ejemplo: Nube Pago es ficticia; no use este formulario para enviar expedientes reales a un modelo externo.</p>
<form action="/audit" method="post" enctype="multipart/form-data">
<label for="files">Documentos</label>
<input id="files" name="files" type="file" multiple required/>
<label for="year">Año del catálogo</label>
<select id="year" name="year"><option value="2026" selected>2026</option><option value="2025">2025</option></select>
<label for="entity">Tipo de entidad</label>
<select id="entity" name="entity">
<option>IFPE</option><option>IFC</option><option>ITF</option>
<option>fintech_general</option><option>plataforma_tecnologica</option>
<option>servicios_digitales</option><option>AV_exchange_non_ef</option>
</select>
<label><input type="checkbox" name="operates_virtual_assets" value="true"/> Opera activos virtuales</label>
<label><input type="checkbox" name="partial_payments" value="true"/> Pagos parciales o diferidos (REP)</label>
<label><input type="checkbox" name="transports_goods" value="true"/> Transporta mercancías (Carta Porte)</label>
<label><input type="checkbox" name="tech_platform" value="true"/> Régimen de plataformas tecnológicas</label>
<label><input type="checkbox" name="digital_services" value="true"/> Servicios digitales LIVA</label>
<label><input type="checkbox" name="use_llm" value="true"/> Revisor LLM (opcional). No lo active con documentos confidenciales: el texto saldría al proveedor configurado en FDH_LLM_BASE_URL. Sin clave, la auditoría sigue siendo solo local.</label>
<button type="submit">Auditar</button>
</form>
<p class="hint">También puede pedir JSON en <code>POST /audit.json</code> con los mismos campos.</p>
</main>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return _FORM


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


def _as_bool(value: str | None) -> bool:
    return (value or "").lower() in {"1", "true", "on", "yes"}


async def _run(
    files: list[UploadFile],
    year: int,
    entity: str,
    operates_virtual_assets: str | None,
    partial_payments: str | None,
    transports_goods: str | None,
    tech_platform: str | None,
    digital_services: str | None,
    use_llm: str | None,
):
    if not files:
        raise ValueError("Suba al menos un documento.")
    profile = Profile(
        entity_type=canonical_entity(entity),
        year=year,
        operates_virtual_assets=_as_bool(operates_virtual_assets),
        has_partial_or_deferred_payments=_as_bool(partial_payments),
        transports_goods=_as_bool(transports_goods),
        is_technological_platform_tax_regime=_as_bool(tech_platform),
        provides_digital_services_liva=_as_bool(digital_services),
    )
    with tempfile.TemporaryDirectory(prefix="fdh-") as tmp:
        folder = Path(tmp)
        saved: list[Path] = []
        for upload in files:
            name = Path(upload.filename or "documento.txt").name
            if not name or name in {".", ".."}:
                continue
            target = folder / name
            data = await upload.read()
            if len(data) > 20 * 1024 * 1024:
                raise ValueError(f"{name} supera 20 MB.")
            target.write_bytes(data)
            saved.append(target)
        if not saved:
            raise ValueError("No llegó ningún archivo con nombre válido.")
        return run_audit(saved, profile, use_llm=_as_bool(use_llm))


@app.post("/audit", response_class=HTMLResponse)
async def audit_html(
    files: list[UploadFile] = File(...),
    year: int = Form(2026),
    entity: str = Form("IFPE"),
    operates_virtual_assets: str | None = Form(None),
    partial_payments: str | None = Form(None),
    transports_goods: str | None = Form(None),
    tech_platform: str | None = Form(None),
    digital_services: str | None = Form(None),
    use_llm: str | None = Form(None),
) -> HTMLResponse:
    try:
        report = await _run(
            files,
            year,
            entity,
            operates_virtual_assets,
            partial_payments,
            transports_goods,
            tech_platform,
            digital_services,
            use_llm,
        )
    except (CatalogError, ValueError) as exc:
        body = f"<h1>No se pudo auditar</h1><pre>{exc}</pre><p>{DISCLAIMER_ES}</p>"
        return HTMLResponse(body, status_code=400)
    return HTMLResponse(render_html(report))


@app.post("/audit.json")
async def audit_json(
    files: list[UploadFile] = File(...),
    year: int = Form(2026),
    entity: str = Form("IFPE"),
    operates_virtual_assets: str | None = Form(None),
    partial_payments: str | None = Form(None),
    transports_goods: str | None = Form(None),
    tech_platform: str | None = Form(None),
    digital_services: str | None = Form(None),
    use_llm: str | None = Form(None),
) -> JSONResponse:
    try:
        report = await _run(
            files,
            year,
            entity,
            operates_virtual_assets,
            partial_payments,
            transports_goods,
            tech_platform,
            digital_services,
            use_llm,
        )
    except (CatalogError, ValueError) as exc:
        return JSONResponse({"error": str(exc), "disclaimer": DISCLAIMER_ES}, status_code=400)
    return JSONResponse(content=json.loads(render_json(report)))
