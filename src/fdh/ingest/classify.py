"""Heuristic document-type classification, with an optional LLM assist.

The LLM may only return labels from the controlled vocabulary. Unknown labels
are dropped. Without a key, classification is purely heuristic.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from fdh.textutil import fold, normalize_text

_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


@dataclass(frozen=True)
class TypeSpec:
    type_id: str
    filename_tokens: tuple[str, ...]
    content_phrases: tuple[str, ...]


# Filename tokens must all appear in the file name. Content phrases are
# multi-word on purpose so a passing mention of "fiscal" or "contrato" does
# not retag the whole file.
SPECS: tuple[TypeSpec, ...] = (
    TypeSpec("aviso_privacidad", ("aviso", "privacidad"), ("aviso de privacidad",)),
    TypeSpec("aviso_privacidad_integral", ("integral",), ("aviso de privacidad integral",)),
    TypeSpec(
        "aviso_privacidad_simplificado",
        ("simplificado",),
        ("aviso de privacidad simplificado",),
    ),
    TypeSpec(
        "politicas_datos",
        ("politica", "datos"),
        ("politica de datos personales", "politica de proteccion de datos"),
    ),
    TypeSpec(
        "procedimientos_arco",
        ("arco",),
        ("procedimiento arco", "procedimiento para ejercer derechos arco"),
    ),
    TypeSpec(
        "politica_seguridad_datos",
        ("seguridad", "datos"),
        ("seguridad de los datos personales",),
    ),
    TypeSpec(
        "politica_seguridad_informacion",
        ("seguridad", "informacion"),
        ("seguridad de la informacion", "politica de seguridad de la informacion"),
    ),
    TypeSpec(
        "plan_respuesta_incidentes",
        ("incidente",),
        ("respuesta a incidentes", "plan de respuesta a incidentes"),
    ),
    TypeSpec(
        "contrato_adhesion",
        ("contrato",),
        ("contrato de adhesion", "contrato de adhesion de"),
    ),
    TypeSpec("caratula", ("caratula",), ("caratula del producto",)),
    TypeSpec("publicidad", ("publicidad",), ("material publicitario", "campana publicitaria")),
    TypeSpec(
        "terminos_plataforma",
        ("terminos",),
        ("terminos y condiciones de la plataforma", "terminos y condiciones"),
    ),
    TypeSpec("website", ("website",), ("pagina publica",)),
    TypeSpec(
        "politica_segregacion",
        ("segregacion",),
        ("segregacion de cuentas", "segregacion de recursos", "separacion de cuentas"),
    ),
    TypeSpec("manual_operaciones", ("manual", "operaciones"), ("manual de operaciones",)),
    TypeSpec("politica_tesoreria", ("tesoreria",), ("politica de tesoreria",)),
    TypeSpec(
        "politica_divulgacion_riesgos",
        ("divulgacion",),
        ("divulgacion de riesgos", "politica de divulgacion"),
    ),
    TypeSpec(
        "listado_comisiones",
        ("comisiones",),
        ("listado de comisiones", "tabla de comisiones"),
    ),
    TypeSpec(
        "manual_riesgos_operativos",
        ("riesgos", "operativos"),
        ("riesgos operativos", "manual de riesgos operativos"),
    ),
    TypeSpec(
        "politica_confidencialidad",
        ("confidencialidad",),
        ("politica de confidencialidad",),
    ),
    TypeSpec(
        "politica_conflictos_interes",
        ("conflicto",),
        ("conflictos de interes", "conflicto de interes"),
    ),
    TypeSpec(
        "politica_prevencion_fraude",
        ("fraude",),
        ("prevencion de fraudes", "prevencion de fraude"),
    ),
    TypeSpec(
        "plan_continuidad",
        ("continuidad",),
        ("plan de continuidad", "continuidad operativa", "continuidad del negocio"),
    ),
    TypeSpec("politica_continuidad", ("politica", "continuidad"), ("politica de continuidad",)),
    TypeSpec(
        "manual_control_interno",
        ("control", "interno"),
        ("manual de control interno", "control interno"),
    ),
    TypeSpec(
        "politica_retencion_documental",
        ("retencion", "documental"),
        ("retencion documental", "conservacion de comprobantes"),
    ),
    TypeSpec("manual_archivo", ("archivo",), ("manual de archivo", "archivo documental")),
    TypeSpec(
        "plan_director_seguridad",
        ("plan", "director"),
        ("plan director de seguridad",),
    ),
    TypeSpec(
        "matriz_cumplimiento",
        ("matriz", "cumplimiento"),
        ("matriz de cumplimiento normativo", "matriz de cumplimiento"),
    ),
    TypeSpec(
        "manual_cumplimiento",
        ("manual", "cumplimiento"),
        ("manual de cumplimiento normativo",),
    ),
    TypeSpec(
        "manual_pld_ft",
        ("pld",),
        ("manual pld", "prevencion de lavado", "manual de prevencion de lavado"),
    ),
    TypeSpec(
        "metodologia_riesgos_pld",
        ("metodologia",),
        ("metodologia de evaluacion de riesgos", "metodologia de riesgos"),
    ),
    TypeSpec("matriz_riesgos_pld", ("matriz", "riesgo"), ("matriz de riesgos pld",)),
    TypeSpec(
        "procedimiento_reportes_uif",
        ("reportes",),
        ("reportes de operaciones relevantes", "procedimiento de reportes"),
    ),
    TypeSpec(
        "politica_kyc",
        ("kyc",),
        ("conocimiento del cliente", "identificacion del cliente"),
    ),
    TypeSpec(
        "procedimiento_onboarding",
        ("onboarding",),
        ("procedimiento de identificacion", "alta del cliente"),
    ),
    TypeSpec(
        "nombramiento_oficial_cumplimiento",
        ("nombramiento",),
        ("nombramiento del oficial de cumplimiento", "oficial de cumplimiento"),
    ),
    TypeSpec("organigrama", ("organigrama",), ("organigrama",)),
    TypeSpec(
        "informe_auditoria_pld",
        ("auditoria",),
        ("informe de auditoria pld", "informe de auditoria"),
    ),
    TypeSpec(
        "procedimiento_lista_bloqueados",
        ("bloquead",),
        ("lista de personas bloqueadas", "personas bloqueadas"),
    ),
    TypeSpec(
        "politica_beneficiario_controlador",
        ("beneficiario",),
        ("beneficiario controlador",),
    ),
    TypeSpec("flujo_onboarding", ("flujo",), ("flujo de contratacion", "flujo de alta")),
    TypeSpec(
        "politica_publicidad",
        ("politica", "publicidad"),
        ("politica de publicidad",),
    ),
    TypeSpec("procedimiento_reus", ("reus",), ("registro de usuarios reus", "consulta al reus")),
    TypeSpec(
        "calendario_cumplimiento_fiscal",
        ("calendario",),
        ("calendario de cumplimiento fiscal", "calendario rmf"),
    ),
    TypeSpec(
        "politica_cfdi",
        ("cfdi",),
        ("politica de facturacion", "emision de cfdi", "factura electronica"),
    ),
    TypeSpec(
        "manual_fiscal",
        ("manual", "fiscal"),
        ("manual fiscal", "manual de cumplimiento fiscal"),
    ),
    TypeSpec("procedimiento_carta_porte", ("carta", "porte"), ("complemento carta porte",)),
    TypeSpec(
        "politica_retenciones",
        ("retencion",),
        ("politica de retenciones", "retencion de isr", "retencion de iva"),
    ),
    TypeSpec(
        "procedimiento_requerimientos_autoridad",
        ("requerimiento",),
        ("requerimientos de autoridad", "articulo 32-b", "articulo 32b"),
    ),
    TypeSpec("politica_iva", ("iva",), ("politica de iva", "iva de servicios digitales")),
)


def vocabulary() -> list[str]:
    return sorted({spec.type_id for spec in SPECS})


def _token_in_name(token: str, folded_name: str) -> bool:
    """Short tokens must be whole words so 'iva' does not match 'privacidad'."""
    needle = fold(token)
    if re.fullmatch(r"[a-z0-9]{2,4}", needle):
        return re.search(rf"\b{re.escape(needle)}\b", folded_name) is not None
    return needle in folded_name


def classify_heuristic(filename: str, text: str) -> list[str]:
    folded_name = fold(filename.replace("_", " ").replace("-", " "))
    folded_text = fold(normalize_text(text))
    matched: list[str] = []
    for spec in SPECS:
        name_hit = bool(spec.filename_tokens) and all(
            _token_in_name(token, folded_name) for token in spec.filename_tokens
        )
        content_hit = any(fold(phrase) in folded_text for phrase in spec.content_phrases)
        # "kyc" files are the onboarding procedure in this vocabulary.
        if spec.type_id == "procedimiento_onboarding" and "kyc" in folded_name:
            name_hit = True
        if name_hit or content_hit:
            matched.append(spec.type_id)
    return matched


def parse_llm_types(raw: str, allowed: set[str]) -> list[str]:
    """Keep only labels that exist in the vocabulary. Never accept invented types."""
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        match = _JSON_OBJECT.search(raw)
        if match is None:
            return []
        try:
            payload = json.loads(match.group(0))
        except json.JSONDecodeError:
            return []
    values = payload.get("types", []) if isinstance(payload, dict) else []
    if not isinstance(values, list):
        return []
    chosen: list[str] = []
    for item in values:
        if isinstance(item, str) and item in allowed and item not in chosen:
            chosen.append(item)
    return chosen


CLASSIFY_SYSTEM = (
    "Clasificas documentos de una fintech mexicana. "
    'Responde SOLO JSON {"types": [...]} usando exclusivamente etiquetas de la '
    "lista proporcionada. No inventes tipos, leyes ni obligaciones. "
    'Si ninguna etiqueta aplica, devuelve {"types": []}.'
)


def classify_with_llm(filename: str, text: str, complete, allowed: set[str]) -> list[str]:
    excerpt = normalize_text(text)[:4000]
    messages = [
        {"role": "system", "content": CLASSIFY_SYSTEM},
        {
            "role": "user",
            "content": (
                "Etiquetas permitidas:\n"
                + ", ".join(sorted(allowed))
                + f"\n\nArchivo: {filename}\nTexto:\n{excerpt}"
            ),
        },
    ]
    try:
        raw = complete(messages)
    except Exception:
        return []
    return parse_llm_types(raw or "", allowed)
