"""Draft policies. Each file says a lawyer must review it before use."""

from __future__ import annotations

from pathlib import Path

_BANNER = """> **BORRADOR DE PLANTILLA.** No es asesoría legal ni una política aprobada.
> Una abogada o un oficial de cumplimiento debe revisarlo contra el texto vigente
> del DOF antes de usarlo. Sustituya los corchetes. Entidad ficticia de ejemplo.
"""

TEMPLATES: dict[str, str] = {
    "manual-pld": _BANNER
    + """
# Manual de PLD/FT — borrador para revisar

Entidad: [razón social ficticia]. Figura: [IFPE/IFC/otra].
Fecha de aprobación: [aaaa-mm-dd]. Órgano: [consejo]. Versión: 1.0.

1. Fundamento: artículo 58 de la LRITF y disposiciones de la CNBV. No pegue este borrador como si ya estuviera presentado.
2. Enfoque basado en riesgos: productos, clientes, zonas y canales. Guarde el resultado de la evaluación.
3. KYC/KYB y beneficiario controlador. PEP con el procedimiento que apruebe cumplimiento.
4. Listas: personas bloqueadas de la SHCP. OFAC y ONU solo como referencia, no como ley mexicana.
5. Monitoreo, alertas y reportes relevantes, inusuales e internos preocupantes, por conducto de la CNBV.
6. Oficial de cumplimiento y comité de comunicación y control.
7. Capacitación y auditoría anual.
8. Conservación de la información de identificación y de los reportes por el plazo que fije la norma leída (el catálogo previo usa diez años).
""",
    "seguridad-informacion": _BANNER
    + """
# Política de seguridad de la información — borrador

Fecha de aprobación: [aaaa-mm-dd].

- Confidencialidad, integridad y disponibilidad. En una IFC, el art. 63 leído hace responsable al director general o al administrador único.
- Accesos con autenticación reforzada para administradores. La sigla MFA no se cita como texto legal.
- Cifrado en tránsito y en reposo, sin fijar un algoritmo que la norma no haya sido leída para imponer.
- Vulnerabilidades, parches, bitácoras y ciclo de desarrollo.
- En IFC, nombrar CISO (art. 65 leído).
- Incidentes IFC, art. 67 leído: aviso inmediato a Ciberseguridad-CNBV@cnbv.gob.mx, cinco días hábiles para la información adicional, quince días hábiles para el plan al concluir, y 48 horas al cliente si hay información sensible. No escriba 72 horas como si fuera ese artículo.
- ISO 27001, NIST CSF 2.0 y SOC 2 son referencia, no obligación mexicana. PCI DSS solo si se procesan tarjetas.
""",
    "continuidad": _BANNER
    + """
# Plan de continuidad — borrador

Fecha de aprobación: [aaaa-mm-dd].

RTO: [horas]. RPO: [horas]. Estas siglas no se presentan como texto de la LRITF; sirven para medir el plan.
Último simulacro: [fecha]. Resultado: [ ]. Evidencia: [ ].
Proveedores críticos y alternativa manual de operación.
""",
    "privacidad": _BANNER
    + """
# Aviso de privacidad — borrador LFPDPPP 2025

Responsable: [razón social]. Domicilio: [ ].

I. Identidad y domicilio del responsable.
II. Datos tratados, y si hay sensibles.
III. Finalidades, distinguiendo las que requieren consentimiento.
IV. Medios para limitar el uso.
V. Mecanismos ARCO y plazos que el procedimiento cite conforme al art. 31.
VI. Cómo se comunican los cambios.

Autoridad: Secretaría Anticorrupción y Buen Gobierno. No cite al INAI como autoridad vigente.
Datos financieros: consentimiento expreso, salvo las excepciones que el abogado confirme en los arts. 9 y 36.
""",
    "quejas": _BANNER
    + """
# Procedimiento de quejas y UNE — borrador

UNE: [nombre], [correo], [teléfono].
Registro del folio, acuse y escalamiento.
RECA: el contrato no se usa sin número de registro.
No fije en este borrador un plazo de días que no haya leído en la disposición.
""",
    "gobierno": _BANNER
    + """
# Gobierno corporativo — borrador

Consejo o administrador único. Comités que el órgano acuerde, con integración y calendario.
Conflictos de interés: abstención, registro y escalamiento.
Código de ética y canal de denuncias.
Terceros y nube: contrato, responsable y si la figura exige autorización de la CNBV.
Fecha de aprobación: [aaaa-mm-dd].
""",
}


def write_templates(out_dir: Path, only: str | None = None) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for key, body in TEMPLATES.items():
        if only and only not in key:
            continue
        path = out_dir / f"{key}.md"
        path.write_text(body.strip() + "\n", encoding="utf-8")
        written.append(path)
    return written
