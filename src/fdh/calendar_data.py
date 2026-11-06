"""Annual obligation reminders.

Dates are reminders. Where the legal text says "within the following month"
the event is placed on day 10 and the description repeats the legal wording.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Obligation:
    uid: str
    month: int
    day: int
    summary: str
    description: str
    entities: tuple[str, ...]
    frequency: str = "YEARLY"
    source_url: str = ""


OBLIGATIONS: tuple[Obligation, ...] = (
    Obligation(
        "fdh-r01-ifpe",
        1,
        10,
        "IFPE: recordatorio de series mensuales (R01 y relacionadas)",
        "El art. 101 de las DCG pide la información dentro del mes inmediato siguiente al cierre. "
        "Este evento es un recordatorio el día 10, no el día legal exacto. "
        "https://dof.gob.mx/nota_detalle_popup.php?codigo=5555030",
        ("IFPE", "ITF"),
        "MONTHLY",
        "https://dof.gob.mx/nota_detalle_popup.php?codigo=5555030",
    ),
    Obligation(
        "fdh-r01-ifc",
        1,
        10,
        "IFC: recordatorio de series mensuales (R01 A-0112 y relacionadas)",
        "El art. 99 de las DCG pide la información dentro del mes inmediato siguiente. "
        "Recordatorio el día 10. "
        "https://dof.gob.mx/nota_detalle_popup.php?codigo=5555030",
        ("IFC", "ITF"),
        "MONTHLY",
        "https://dof.gob.mx/nota_detalle_popup.php?codigo=5555030",
    ),
    Obligation(
        "fdh-r13-trimestral",
        1,
        20,
        "ITF: recordatorio de reportes trimestrales R13 y R27",
        "Los arts. 99-II y 101-II piden esos reportes dentro del mes siguiente al cierre del trimestre. "
        "https://dof.gob.mx/nota_detalle_popup.php?codigo=5555030",
        ("IFPE", "IFC", "ITF"),
        "MONTHLY",
        "https://dof.gob.mx/nota_detalle_popup.php?codigo=5555030",
    ),
    Obligation(
        "fdh-capital-cierre",
        12,
        15,
        "Revisar capital mínimo suscrito y pagado",
        "El art. 8 de las DCG pide el capital suscrito y pagado a más tardar el último día hábil del año, "
        "con la UDI del 31 de diciembre anterior. "
        "https://dof.gob.mx/nota_detalle_popup.php?codigo=5537450",
        ("IFPE", "IFC", "ITF"),
        source_url="https://dof.gob.mx/nota_detalle_popup.php?codigo=5537450",
    ),
    Obligation(
        "fdh-rmf",
        1,
        15,
        "Releer la RMF del ejercicio y sus modificaciones",
        "La RMF se publica al cierre del año previo y se modifica durante el ejercicio. "
        "https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/normatividad_rmf_rgce2026.html",
        ("IFPE", "IFC", "ITF", "fintech_general", "SOFOM_ENR"),
        source_url="https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/normatividad_rmf_rgce2026.html",
    ),
    Obligation(
        "fdh-pld-auditoria",
        3,
        31,
        "Cerrar la auditoría anual de PLD/FT",
        "El catálogo previo exige una revisión anual de PLD. Confirme el calendario interno contra las DCG del art. 58.",
        ("IFPE", "IFC", "ITF"),
        source_url="https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf",
    ),
    Obligation(
        "fdh-pld-capacitacion",
        11,
        30,
        "Cerrar la capacitación de PLD/FT del año",
        "Conserve constancias. La periodicidad fina de la reforma LFPIORPI está UNVERIFIED en el catálogo.",
        ("IFPE", "IFC", "ITF", "SOFOM_ENR", "transmisor_dinero"),
        source_url="https://www.diputados.gob.mx/LeyesBiblio/ref/lfpiorpi/LFPIORPI_ref03_16jul25.pdf",
    ),
    Obligation(
        "fdh-dictamen",
        4,
        30,
        "Dictamen de estados financieros del ejercicio anterior",
        "Conserve el dictamen del auditor externo. El número de artículo de la LRITF está UNVERIFIED en la ficha financiero-auditor-externo.",
        ("IFPE", "IFC", "ITF"),
        source_url="https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf",
    ),
    Obligation(
        "fdh-continuidad",
        6,
        30,
        "Probar el plan de continuidad y anotar RTO/RPO",
        "La ficha de continuidad medida está UNVERIFIED en cuanto a las siglas. El recordatorio pide evidencia de la prueba.",
        ("IFPE", "IFC", "ITF"),
        source_url="https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf",
    ),
    Obligation(
        "fdh-privacidad",
        3,
        21,
        "Revisar el aviso de privacidad frente a la LFPDPPP 2025",
        "Confirme que no cite al INAI como autoridad vigente. "
        "https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf",
        ("IFPE", "IFC", "ITF", "fintech_general"),
        source_url="https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf",
    ),
)


def obligations_for(entity: str) -> list[Obligation]:
    return [item for item in OBLIGATIONS if _matches(entity, item)]


def _matches(entity: str, item: Obligation) -> bool:
    if entity in item.entities:
        return True
    return entity == "ITF" and bool({"IFPE", "IFC"} & set(item.entities))


def render_ics(entity: str, year: int) -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//fintech-documentation-help//ES",
        "CALSCALE:GREGORIAN",
        "X-WR-CALNAME:Obligaciones fintech (recordatorios, no asesoria)",
    ]
    for item in obligations_for(entity):
        stamp = f"{year:04d}{item.month:02d}{item.day:02d}"
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{item.uid}-{year}@fintech-documentation-help",
                f"DTSTART;VALUE=DATE:{stamp}",
                f"SUMMARY:{_ics(item.summary)}",
                f"DESCRIPTION:{_ics(item.description)}",
                f"RRULE:FREQ={item.frequency}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    return "\n".join(lines) + "\n"


def _ics(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")
