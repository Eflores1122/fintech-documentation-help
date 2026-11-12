# Fuentes

Fecha de la pasada de esta versión: **2026-11-06**. Cada regla del catálogo trae su `source_url`, `source_name`, `effective_date` y `last_verified`. Si el artículo o el número de regla no se leyó, la ficha tiene `unverified: true` (y `verified: false`) más `unverified_detail`. No se rellena el hueco.

`fdh rules citations` imprime las reglas que no traen URL https de un sitio oficial, nombre de fuente o fecha, y sale con error. No propone otra URL. UNVERIFIED no es lo mismo: ahí la URL y las fechas sí están, y el artículo no leído sigue en blanco.

## Leídas en esta pasada (texto, no solo el índice)

| Instrumento | Qué se usó | URL |
|---|---|---|
| DCG de ITF, capital y efectivo | Arts. 6, 7, 8 y 9 (500,000 / 700,000 UDI; suscrito y pagado; 10,000 UDI mensuales y 1,500 UDI diarias de efectivo) | https://dof.gob.mx/nota_detalle_popup.php?codigo=5537450 |
| Resolución que modifica las DCG, firmada el 14-mar-2019 | Arts. 63, 65, 67, 85 (inicio), 98 a 103. Reportes A-0111 / A-0112, SITI, `cesiti@cnbv.gob.mx`. El art. 67 de IFC: aviso inmediato, cinco días hábiles, quince días hábiles y 48 horas al cliente. No aparece un plazo de 72 horas. | https://dof.gob.mx/nota_detalle_popup.php?codigo=5555030 |
| Resolución de criterios contables y reportes, DOF 9-sep-2025 | Transitorio único: entra en vigor el 1 de enero de 2026. Sustituye criterios de los anexos 6 y 7. No se transcribieron las celdas. | https://dof.gob.mx/2025/SHCP/SHCP_090925.pdf |
| NOM-151-SCFI-2016 | Conservación de mensajes de datos por un prestador de servicios de certificación. DOF 30-mar-2017. | https://www.dof.gob.mx/nota_detalle.php?codigo=5478024&fecha=30%2F03%2F2017 |
| Circular 4/2019 de Banxico | Disposición 3.a: operaciones con activos virtuales solo internas y sin transmitir el riesgo al cliente. El resto de la circular no se lineó. | PDF en el portal de Banxico ligado desde la ficha |
| Circular 12/2018 y Circular 14/2017 | Se confirmó la ficha oficial. Los numerales no se leyeron uno a uno: esas reglas están UNVERIFIED. | Portal de Banxico |

## Ya citadas por el catálogo previo y no releídas línea a línea el 2026-11-06

LRITF, LFPDPPP 2025, LFPIORPI reforma 16-jul-2025, LIF 2026, RMF 2026 (hub y PDF del DOF), disposiciones de transparencia de CONDUSEF, disposiciones IFPE del 28-ene-2021. Donde una ficha nueva usa un número de artículo que no se releyó, está UNVERIFIED aunque el catálogo viejo ya lo diera por citado.

## Referencia internacional (no obligatoria en México)

ISO/IEC 27001:2022, ISO 19011:2018, NIST CSF 2.0, PCI DSS 4.0, SOC 2, COSO y GAFI/FATF. Las reglas que los usan tienen `binding: false` y severidad `info`, salvo las de metodología del modo estricto, que sí restan puntaje y lo dicen en la causa.

## Lo que esta pasada no cerró

- Números de regla de la RMF 2026 (DIOT, contabilidad electrónica, CFDI).
- Fracción vigente del CFF para el beneficiario controlador fiscal.
- Artículos de autorización, objeto social, comités, poderes, modelos novedosos, APIs del 4-jun-2020, Circular 12/2018 artículo por artículo, plazos de incidente de las IFPE, REPSE artículo por artículo, plazos de queja de CONDUSEF, CAT/GAT y estados de cuenta.
- Listado completo del art. 85 (servicios con terceros que requieren autorización de la CNBV).
- Celdas de los anexos de reportes y de estimaciones.

La vigilancia semanal (`fdh rules watch` y la acción de GitHub) solo avisa si cambia el hash de una página oficial. No redacta reglas.
