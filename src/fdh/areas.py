"""Area labels and the audit procedure for each compliance domain.

The steps are an audit method. They do not add legal duties beyond the rules.
"""

from __future__ import annotations

AREA_LABELS: dict[str, str] = {
    "legal": "Legal y corporativo",
    "regulatorio": "Regulatorio CNBV y Banxico",
    "financiero": "Financiero y contable",
    "fiscal": "Fiscal (SAT)",
    "pld": "PLD/FT",
    "ciberseguridad": "Seguridad de la información y ciberseguridad",
    "privacidad": "Protección de datos personales",
    "condusef": "Protección al usuario (CONDUSEF)",
    "riesgos": "Riesgos y control interno",
    "operacion": "Operación y TI",
    "laboral": "Laboral y recursos humanos",
    "metodologia": "Criterios del modo estricto",
    "meta": "Meta de la herramienta",
}

AREA_PROCEDURES: dict[str, list[str]] = {
    "legal": [
        "Confirmar la figura (IFPE, IFC, SOFOM ENR, transmisor, asesor o modelo novedoso) y el alcance autorizado.",
        "Leer estatutos, poderes, actas y contratos con terceros contra el oficio, si existe.",
        "Revisar firma electrónica y conservación de mensajes solo con la NOM citada, sin ampliarla.",
        "Separar lo que es ley de lo que el expediente no trae. No completar artículos no leídos.",
    ],
    "regulatorio": [
        "Fijar el año del catálogo y el perfil (activos virtuales, SPEI, crédito, rendimiento).",
        "Contrastar capital, límites y calendario de reportes con la disposición citada.",
        "Verificar que el calendario diga SITI y el reporte de la figura (A-0111 o A-0112), no un día inventado.",
        "Si la regla está UNVERIFIED, el hallazgo se reporta pero no se trata como texto cerrado.",
    ],
    "financiero": [
        "Identificar el marco: criterios CNBV del ejercicio, no una NIF suelta.",
        "Pedir estados financieros, dictamen del auditor externo, conciliaciones y notas.",
        "Para 2026, buscar la resolución del 9 de septiembre de 2025 y la vigencia del 1 de enero de 2026.",
        "No recalcular reservas: solo ver si el documento describe el control.",
    ],
    "fiscal": [
        "Anclar el expediente a la RMF del ejercicio y a la LIF cuando la figura sea IFC.",
        "Revisar CFDI 4.0, retenciones, DIOT, contabilidad electrónica y opinión de cumplimiento.",
        "Tratar al beneficiario controlador fiscal aparte del de PLD y no fijar la fracción si la ficha dice UNVERIFIED.",
        "Dejar fuera Carta Porte, plataformas y servicios digitales si el perfil no los activa.",
    ],
    "pld": [
        "Leer el manual, la metodología de riesgos, el alta de cliente y el monitoreo como un solo flujo.",
        "Confirmar oficial de cumplimiento, comité, capacitación, listas y reportes relevantes, inusuales e internos preocupantes.",
        "Medir la conservación contra diez años solo donde la ficha ya lo trae verificado.",
        "Marcar OFAC y GAFI como referencia, no como ley mexicana.",
    ],
    "ciberseguridad": [
        "Distinguir IFC (arts. 63, 65 y 67 leídos) de IFPE (plazos de incidente no copiados del art. 67).",
        "Revisar accesos, cifrado, vulnerabilidades, bitácoras, desarrollo, APIs y nube.",
        "Exigir en el plan de incidentes los plazos que la ficha marca como leídos y rechazar 72 horas como si fueran el texto del art. 67.",
        "Pedir RTO, RPO y prueba como evidencia de que la continuidad está medida, con la ficha UNVERIFIED visible.",
    ],
    "privacidad": [
        "Desarmar el aviso contra los seis elementos del art. 15.",
        "Rechazar al INAI como autoridad vigente y buscar a la Secretaría Anticorrupción y Buen Gobierno.",
        "Revisar ARCO, encargados, transferencias y el aviso a titulares si hay una vulneración significativa.",
        "No exigir el listado de transferencias como elemento mínimo del art. 15.",
    ],
    "condusef": [
        "Buscar RECA antes del uso, consentimiento expreso y leyendas de la carátula.",
        "Revisar UNE, REUS, comisiones y estados de cuenta.",
        "Activar CAT solo si el perfil ofrece crédito y GAT solo si ofrece rendimiento.",
        "No inventar el plazo de queja si la ficha está UNVERIFIED.",
    ],
    "riesgos": [
        "Leer la matriz: riesgo, causa, control, responsable y residual.",
        "Separar riesgo operacional, tecnológico, legal, de liquidez (IFPE) y de crédito (IFC).",
        "Contrastar la auditoría interna con la auditoría anual de PLD: no son el mismo informe.",
        "Dejar las tres líneas y COSO como referencia, no como artículo de la ley.",
    ],
    "operacion": [
        "Revisar cambios a producción, inventario de activos y contratos con niveles de servicio.",
        "Ver que la queja operativa tenga folio, además del procedimiento de la UNE.",
        "No dar por probada la continuidad si no hay fecha de simulacro en el plan.",
    ],
    "laboral": [
        "Activar REPSE solo si el perfil declara servicios especializados.",
        "Separar la capacitación laboral de la capacitación de PLD.",
        "Leer el código de ética y el canal de denuncias, con fecha de aprobación en modo estricto.",
    ],
    "metodologia": [
        "Estas reglas solo corren en --strictness max, que es el default.",
        "Penalizan falta de fecha de aprobación, placeholders, versiones de trabajo y controles que admiten no tener evidencia.",
        "No son normas mexicanas. El informe debe decirlo.",
        "Con --strictness standard o high quedan fuera del dictamen.",
    ],
    "meta": [
        "No se auditan contra el expediente del cliente.",
    ],
}


def area_label(area: str) -> str:
    return AREA_LABELS.get(area, area)
