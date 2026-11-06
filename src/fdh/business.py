"""Infer what the fintech does before scoring. The CLI entity stays authoritative."""

from __future__ import annotations

from fdh.models import Document

# Signals are multi-word on purpose. "nube" alone matches the fictional name Nube Pago.
_PRODUCTS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "wallet",
        "Cuenta o wallet de fondos de pago electrónico",
        ("dinero electrónico", "fondos de pago electrónico", "wallet"),
    ),
    ("remesas", "Remesas", ("remesa", "envío de dinero al extranjero")),
    (
        "tarjetas",
        "Emisión o procesamiento de tarjetas",
        (
            "emisión de tarjetas",
            "emision de tarjetas",
            "tarjeta de débito",
            "tarjeta de debito",
            "pci dss",
        ),
    ),
    (
        "credito",
        "Crédito o financiamiento",
        (
            "riesgo de crédito",
            "riesgo de credito",
            "otorgamiento de crédito",
            "otorgamiento de credito",
        ),
    ),
    (
        "inversion",
        "Inversión o asesoría",
        ("asesor en inversiones", "asesoría de inversión", "asesoria de inversion"),
    ),
    ("cripto", "Activos virtuales", ("activo virtual", "activos virtuales", "cripto")),
    ("crowdfunding", "Financiamiento colectivo", ("financiamiento colectivo", "crowdfunding")),
    ("transfronterizo", "Pagos transfronterizos", ("transfronteriz", "moneda extranjera")),
    ("spei", "SPEI", ("spei",)),
    ("codi", "CoDi", ("codi",)),
    ("open_banking", "APIs u open banking", ("open banking", "interfaces de programación")),
)

_CUSTODY = (
    "recursos de los clientes",
    "recursos de clientes",
    "segregación de",
    "segregacion de",
    "dinero electrónico",
)
_CLOUD = (
    "proveedor de nube",
    "computación en la nube",
    "computacion en la nube",
    "amazon web services",
    "microsoft azure",
)
_SENSITIVE = ("dato sensible", "datos sensibles", "biométric", "biometric")
_CHANNELS = (
    ("app", ("aplicación móvil", "aplicacion movil", "app ")),
    ("web", ("plataforma", "sitio web", "página")),
    ("efectivo", ("efectivo",)),
)


def infer_business(
    documents: list[Document],
    declared_entity: str,
    questionnaire: dict[str, object] | None = None,
) -> dict[str, object]:
    blob_parts: list[tuple[str, str]] = []
    for doc in documents:
        if doc.text:
            blob_parts.append((doc.path, doc.text.casefold()))
    products: list[dict[str, object]] = []
    for key, label, phrases in _PRODUCTS:
        hit = _first(blob_parts, phrases)
        forced = bool(questionnaire and questionnaire.get(key))
        if hit or forced:
            products.append(
                {
                    "id": key,
                    "label": label,
                    "evidence": hit[1] if hit else "Declarado en el cuestionario.",
                    "document": hit[0] if hit else None,
                    "source": "cuestionario" if forced and not hit else "documento",
                }
            )
    custody = _first(blob_parts, _CUSTODY)
    cloud = _first(blob_parts, _CLOUD)
    sensitive = _first(blob_parts, _SENSITIVE)
    channels = []
    for key, phrases in _CHANNELS:
        hit = _first(blob_parts, phrases)
        if hit:
            channels.append({"id": key, "evidence": hit[1], "document": hit[0]})
    suggested = _suggest_entity(products, declared_entity)
    coherence = _coherence(products, documents, blob_parts)
    return {
        "declared_entity": declared_entity,
        "suggested_entity": suggested,
        "products": products,
        "channels": channels,
        "custodies_client_funds": custody is not None,
        "custody_evidence": None
        if custody is None
        else {"document": custody[0], "quote": custody[1]},
        "cloud": cloud is not None,
        "cloud_evidence": None if cloud is None else {"document": cloud[0], "quote": cloud[1]},
        "sensitive_data": sensitive is not None,
        "sensitive_evidence": None
        if sensitive is None
        else {"document": sensitive[0], "quote": sensitive[1]},
        "volumes": "No inferido: el expediente no trae un volumen cuantificado y no se inventa.",
        "coherence": coherence,
        "diagram": _diagram(declared_entity, products, custody is not None),
        "note": (
            "El tipo declarado en la auditoría no se sustituye por la inferencia. "
            "Esto no es asesoría legal ni fiscal."
        ),
    }


def _suggest_entity(products: list[dict[str, object]], declared: str) -> str:
    ids = {str(item["id"]) for item in products}
    if "crowdfunding" in ids:
        return "IFC"
    if "wallet" in ids:
        return "IFPE"
    if "inversion" in ids and "wallet" not in ids:
        return "asesor_inversion"
    return declared


def _coherence(
    products: list[dict[str, object]],
    documents: list[Document],
    parts: list[tuple[str, str]],
) -> list[dict[str, str]]:
    text = "\n".join(body for _, body in parts)
    types = {label for doc in documents for label in doc.types}
    ids = {str(item["id"]) for item in products}
    rows: list[dict[str, str]] = []
    if "tarjetas" in ids and "pci" not in text and "politica_pci" not in types:
        rows.append(
            {
                "id": "coherencia-tarjetas-sin-pci",
                "message": (
                    "El expediente habla de tarjetas y no aparece PCI DSS ni un contrato con el emisor. "
                    "PCI no es ley mexicana; si se procesan tarjetas, el hueco es de control."
                ),
            }
        )
    if (
        "wallet" in ids
        and "politica_segregacion" not in types
        and "segregación de" not in text
        and "segregacion de" not in text
    ):
        rows.append(
            {
                "id": "coherencia-wallet-sin-segregacion",
                "message": (
                    "Hay cuenta de dinero electrónico y no hay política de segregación de recursos de clientes."
                ),
            }
        )
    if (
        "crowdfunding" in ids
        and "politica_retenciones" not in types
        and "retención" not in text
        and "retencion" not in text
    ):
        rows.append(
            {
                "id": "coherencia-ifc-sin-retencion",
                "message": (
                    "El negocio es financiamiento colectivo y no aparece el procedimiento de retención de la LIF."
                ),
            }
        )
    if (
        "cripto" in ids
        and "politica_activos_virtuales" not in types
        and "operación interna" not in text
        and "operacion interna" not in text
    ):
        rows.append(
            {
                "id": "coherencia-cripto-sin-politica",
                "message": (
                    "Hay activos virtuales y no aparece la restricción de operación interna de la Circular 4/2019."
                ),
            }
        )
    return rows


def _diagram(entity: str, products: list[dict[str, object]], custody: bool) -> str:
    labels = [str(item["label"]) for item in products] or [
        "Actividad no identificada en el expediente"
    ]
    lines = ["flowchart LR", f"  cliente[Cliente] --> entidad[{entity}]"]
    for index, label in enumerate(labels[:6]):
        safe = "".join(ch for ch in label if ch.isalnum() or ch == " ")[:40]
        lines.append(f"  entidad --> p{index}[{safe}]")
    if custody:
        lines.append("  entidad --> fondos[Recursos de clientes]")
    lines.append("  entidad --> docs[Expediente documental]")
    return "\n".join(lines)


def _first(parts: list[tuple[str, str]], phrases: tuple[str, ...]) -> tuple[str, str] | None:
    for path, text in parts:
        for phrase in phrases:
            needle = phrase.casefold()
            at = text.find(needle)
            if at < 0:
                continue
            start = max(0, at - 40)
            end = min(len(text), at + len(needle) + 40)
            quote = text[start:end].replace("\n", " ").strip()
            return path, quote
    return None
