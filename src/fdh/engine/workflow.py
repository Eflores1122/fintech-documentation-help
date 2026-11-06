"""Planning, inventory, remediation, opinion and follow-up for one audit."""

from __future__ import annotations

from fdh.areas import AREA_PROCEDURES, area_label
from fdh.models import SEVERITY_RANK, AuditReport, Document, Finding, Profile, Rule

_EFFECT = {
    "critical": (
        "El vacío puede impedir acreditar la obligación ante la autoridad o frente al cliente."
    ),
    "high": "La omisión es material: una revisión exigente no daría por existente el control.",
    "medium": "El control está incompleto o ambiguo y el modo estricto no lo acepta.",
    "low": "La claridad del expediente es insuficiente.",
    "info": "Recordatorio visible. No mueve el puntaje.",
}


def decorate(rule: Rule, finding: Finding) -> None:
    """Fill the formal observation. Deterministic severity stays as cataloged."""
    finding.area = rule.area or finding.area
    finding.binding = rule.binding
    finding.verified = not rule.unverified
    finding.recommendation = rule.fix_suggestion
    finding.suggested_owner = rule.owner_role
    finding.suggested_deadline = (
        f"{rule.remediation_days} días naturales desde la fecha del informe"
    )
    finding.evidence_required = list(rule.evidence_expected) or [
        f"Documento clasificado como {name}." for name in rule.documents
    ]
    finding.criterion = f"{rule.requirement} Fuente: {rule.source_name}."
    if finding.status == "pass":
        finding.condition = "El texto revisado cubre el criterio determinístico."
        finding.cause = "Se localizó el soporte pedido por la regla."
        finding.effect = "No se abre observación por este criterio."
        return
    if finding.status == "not_applicable":
        finding.condition = finding.message
        finding.cause = "El perfil declarado deja la regla fuera de alcance."
        finding.effect = "Queda fuera del puntaje."
        return
    finding.condition = finding.message
    finding.cause = _cause(finding.message)
    if not rule.binding:
        finding.cause += " El criterio es de auditoría o de referencia, no una norma mexicana."
    if rule.unverified:
        finding.cause += (
            " La ficha está UNVERIFIED: no se trate el número de artículo como cerrado."
        )
    finding.effect = _EFFECT[rule.severity]


def _cause(message: str) -> str:
    if message.startswith("No se encontró ningún documento"):
        return "El expediente no trae el documento que la regla espera."
    if "Faltan elementos" in message or "No aparece" in message:
        return "El documento existe, pero no acredita el criterio o le falta un elemento."
    if "Se encontró" in message:
        return "El documento contiene una expresión incompatible con el criterio."
    if "No coincide" in message:
        return "El patrón exigido no aparece."
    return "El contenido revisado no acredita el criterio."


def build_inventory(rules: list[Rule], documents: list[Document], profile: Profile) -> list[dict]:
    expected: dict[str, list[str]] = {}
    for rule in rules:
        if "tool" in rule.entity_types and not rule.applies_to_entity(profile.entity_type):
            continue
        if not rule.applies_to_entity(profile.entity_type):
            continue
        if not rule.enabled_at(profile.strictness):
            continue
        if rule.applies_if and not profile.flag(rule.applies_if):
            continue
        for name in rule.documents:
            expected.setdefault(name, []).append(rule.id)
    present: dict[str, list[str]] = {}
    for doc in documents:
        for label in doc.types:
            present.setdefault(label, []).append(doc.path)
    rows = []
    for name in sorted(expected):
        rows.append(
            {
                "document_type": name,
                "present": name in present,
                "files": present.get(name, []),
                "rules": expected[name],
            }
        )
    return rows


def build_remediation(findings: list[Finding]) -> list[dict]:
    rows = []
    for finding in findings:
        if finding.status != "fail":
            continue
        rows.append(
            {
                "rule_id": finding.rule_id,
                "title": finding.title,
                "severity": finding.severity,
                "area": finding.area,
                "owner": finding.suggested_owner,
                "deadline": finding.suggested_deadline,
                "recommendation": finding.recommendation or finding.fix_suggestion,
                "status": "abierto",
                "evidence_required": list(finding.evidence_required),
                "binding": finding.binding,
                "verified": finding.verified,
            }
        )
    rows.sort(key=lambda item: (SEVERITY_RANK[str(item["severity"])], str(item["rule_id"])))
    return rows


def build_opinion(report_summary: dict[str, int], overall: float | None) -> dict[str, object]:
    critical = report_summary.get("fail_critical", 0)
    high = report_summary.get("fail_high", 0)
    nonbinding = report_summary.get("fail_nonbinding", 0)
    if critical:
        label = "adverso"
        narrative = (
            "Hay incumplimientos críticos. En el modo de auditor estricto el dictamen "
            "documental no puede ser limpio."
        )
    elif high:
        label = "con salvedades"
        narrative = "No hay críticos abiertos, pero hay hallazgos altos."
    elif overall is not None and overall >= 90 and report_summary.get("fail", 0) == 0:
        label = "limpio documental"
        narrative = "Los criterios ponderados del expediente revisado quedaron cubiertos."
    else:
        label = "con observaciones"
        narrative = "El expediente tiene observaciones que impiden un dictamen limpio."
    if nonbinding:
        narrative += (
            f" {nonbinding} hallazgos no son norma mexicana: son criterio de auditoría "
            "o marco de referencia."
        )
    return {
        "label": label,
        "overall": overall,
        "narrative": narrative,
        "certified_audit": False,
        "disclaimer": (
            "Esto no es un dictamen de auditor externo ni una opinión legal. "
            "Es la calificación documental de esta herramienta."
        ),
    }


def build_phases(profile: Profile, inventory: list[dict], summary: dict[str, int]) -> list[dict]:
    missing = sum(1 for row in inventory if not row["present"])
    present = sum(1 for row in inventory if row["present"])
    steps = [
        (
            "planeacion",
            "Planeación",
            f"Entidad {profile.entity_type}, catálogo {profile.year}, estrictez {profile.strictness}.",
        ),
        (
            "inventario",
            "Inventario",
            f"{present} tipos de documento presentes y {missing} esperados ausentes.",
        ),
        (
            "revision_documental",
            "Revisión documental",
            "Chequeos determinísticos del catálogo del año. La IA, si se enciende, no baja severidad.",
        ),
        (
            "pruebas_controles",
            "Pruebas de controles",
            "Cédula de evidencia marcada por el usuario, si se entregó. Un «presente» no borra un fallo.",
        ),
        (
            "hallazgos",
            "Hallazgos",
            f"{summary.get('fail', 0)} incumplimientos, {summary.get('pass', 0)} cumplimientos.",
        ),
        (
            "remediacion",
            "Plan de remediación",
            "Cada incumplimiento queda abierto, con responsable y plazo sugeridos.",
        ),
        (
            "seguimiento",
            "Seguimiento",
            "Compare este informe con el anterior mediante --compare. Lo nuevo no hereda un pass viejo.",
        ),
        (
            "dictamen",
            "Dictamen",
            "Calificación por área y global. No sustituye una auditoría certificada.",
        ),
    ]
    return [{"id": key, "title": title, "summary": text} for key, title, text in steps]


def build_heatmap(findings: list[Finding], by_area: dict[str, float | None]) -> dict[str, dict]:
    heat: dict[str, dict] = {}
    for finding in findings:
        if not finding.area or finding.status == "not_applicable":
            continue
        cell = heat.setdefault(
            finding.area,
            {
                "label": area_label(finding.area),
                "score": by_area.get(finding.area),
                "fail": 0,
                "critical": 0,
                "pass": 0,
                "unverified_fail": 0,
            },
        )
        if finding.status == "fail":
            cell["fail"] += 1
            if finding.severity == "critical":
                cell["critical"] += 1
            if not finding.verified:
                cell["unverified_fail"] += 1
        elif finding.status == "pass":
            cell["pass"] += 1
    for area, cell in heat.items():
        cell["score"] = by_area.get(area)
        cell["procedure"] = AREA_PROCEDURES.get(area, [])
    return dict(sorted(heat.items()))


def apply_evidence(findings: list[Finding], marks: dict[str, str]) -> None:
    """A checklist mark never turns a deterministic fail into a pass."""
    for finding in findings:
        mark = (marks.get(finding.rule_id) or "").strip().lower()
        if mark not in {"present", "presente", "absent", "ausente", "partial", "parcial"}:
            continue
        if mark in {"absent", "ausente"} and finding.status == "pass":
            finding.status = "fail"
            finding.message += " La cédula de evidencia marca el soporte como ausente."
            finding.condition = finding.message
            finding.cause = (
                "El usuario no aportó la evidencia del control, aunque el texto coincidió."
            )
            if "evidence_checklist" not in finding.origin:
                finding.origin.append("evidence_checklist")
        elif mark in {"partial", "parcial"} and finding.status == "pass":
            finding.status = "unclear"
            finding.message += " La cédula de evidencia está parcial."
            finding.condition = finding.message
            if "evidence_checklist" not in finding.origin:
                finding.origin.append("evidence_checklist")
        elif mark in {"present", "presente"} and finding.status == "fail":
            extra = " La cédula dice presente; el chequeo determinístico sigue en incumplimiento."
            finding.notes = (finding.notes or "") + extra


def compare_with(previous: dict, findings: list[Finding]) -> list[dict]:
    before = {
        str(item.get("rule_id")): str(item.get("status"))
        for item in previous.get("findings", [])
        if isinstance(item, dict)
    }
    rows = []
    current_ids = set()
    for finding in findings:
        current_ids.add(finding.rule_id)
        prior = before.get(finding.rule_id)
        rows.append(
            {
                "rule_id": finding.rule_id,
                "before": prior,
                "after": finding.status,
                "changed": prior != finding.status,
                "area": finding.area,
                "severity": finding.severity,
            }
        )
    for rule_id, status in sorted(before.items()):
        if rule_id not in current_ids:
            rows.append(
                {
                    "rule_id": rule_id,
                    "before": status,
                    "after": None,
                    "changed": True,
                    "area": "",
                    "severity": "",
                }
            )
    return rows


def summary_extras(findings: list[Finding], base: dict[str, int]) -> dict[str, int]:
    base["fail_nonbinding"] = sum(
        1 for item in findings if item.status == "fail" and not item.binding
    )
    base["fail_unverified"] = sum(
        1 for item in findings if item.status == "fail" and not item.verified
    )
    return base


def opinion_ready(report: AuditReport) -> str:
    label = str(report.opinion.get("label", ""))
    return label
