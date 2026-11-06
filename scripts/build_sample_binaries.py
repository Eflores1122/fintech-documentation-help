"""Regenerate the synthetic PDF and DOCX shipped under samples/nube_pago/docs."""

from pathlib import Path

import docx

from fdh.ingest.pdfutil import write_simple_pdf

ROOT = Path(__file__).resolve().parents[1] / "samples" / "nube_pago" / "docs"
BANNER = (
    "DOCUMENTO FICTICIO DE DEMOSTRACION - Nube Pago, S.A. de C.V., IFPE imaginaria. "
    "No corresponde a ninguna entidad autorizada."
)


def main() -> None:
    write_simple_pdf(
        ROOT / "publicidad_campana.pdf",
        "\n".join(
            [
                BANNER,
                "",
                "MATERIAL PUBLICITARIO",
                "Abre tu cuenta de dinero electronico con Nube Pago.",
                "Tus recursos estan seguros con nosotros.",
                "Campana ficticia, sin leyendas legales.",
            ]
        ),
    )
    document = docx.Document()
    document.add_paragraph(
        "DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. "
        "No corresponde a ninguna entidad autorizada."
    )
    document.add_heading("Nombramiento del oficial de cumplimiento", level=1)
    document.add_paragraph("El puesto de oficial de cumplimiento está vacante.")
    document.add_paragraph("La entidad ficticia no cuenta con certificación CNBV para ese puesto.")
    table = document.add_table(rows=2, cols=2)
    table.rows[0].cells[0].text = "Puesto"
    table.rows[0].cells[1].text = "Estado"
    table.rows[1].cells[0].text = "Oficial de cumplimiento"
    table.rows[1].cells[1].text = "Vacante, sin certificación"
    document.save(ROOT / "nombramiento_oficial_cumplimiento.docx")
    print("binaries written")


if __name__ == "__main__":
    main()
