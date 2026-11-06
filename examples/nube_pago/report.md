# Auditoría documental 2026 — IFPE

> **AVISO: Este reporte no es asesoría legal ni fiscal. Es un checklist asistido que cita fuentes públicas con fecha de verificación. Las reglas marcadas UNVERIFIED requieren lectura íntegra del instrumento oficial antes de tratarlas como definitivas. Toda decisión de cumplimiento debe validarse con un abogado o contador autorizado y contra el texto vigente en el Diario Oficial de la Federación y los portales oficiales (SAT, CNBV, Banxico, CONDUSEF, UIF, Cámara de Diputados).**
>
> This output is not legal or tax advice. It is an assisted checklist citing public sources and a verification date. Rules flagged UNVERIFIED still need a full read of the official instrument. Compliance decisions must be confirmed by a qualified lawyer or accountant against the current official text.

- Herramienta: fintech-documentation-help 0.1.0
- Generado (UTC): 2026-11-05T18:00:00+00:00
- Entidad: `IFPE` · catálogo 2026
- LLM: no

## Puntaje

**General:** 7.6 / 100

| Dominio | Puntaje |
|---|---:|
| Banxico / IFPE | 0.0 |
| CNBV | n/a |
| CONDUSEF | 0.0 |
| LRITF | 9.7 |
| PLD/FT | 12.2 |
| Datos personales (LFPDPPP) | 9.5 |
| SAT / fiscal | 0.0 |

## Resumen

- Cumple: 3 · Incumplimiento: 35 · No aplica: 5 · No concluyente: 0
- Fallas por severidad: critical 13, high 15, medium 6, low 0, info 1
- Reglas UNVERIFIED visibles en este reporte: 3
- Reglas omitidas por tipo de entidad o por ser internas: 3

## Documentos ingeridos

- `aviso_de_privacidad.md` → aviso_privacidad
- `caratula_cuenta.md` → caratula
- `contrato_adhesion.md` → contrato_adhesion
- `manual_pld_ft.md` → manual_pld_ft
- `nombramiento_oficial_cumplimiento.docx` → nombramiento_oficial_cumplimiento
- `politica_cfdi.md` → politica_cfdi
- `politica_conflictos_interes.md` → politica_conflictos_interes
- `procedimiento_kyc.txt` → politica_kyc, procedimiento_onboarding
- `publicidad_campana.pdf` → publicidad
- `terminos_plataforma.md` → terminos_plataforma

## Hallazgos

### Incumplimiento · critical · `banxico-ifpe-continuidad-seguridad`

**IFPE — política estratégica de continuidad y seguridad**

No se encontró ningún documento clasificado como: politica_continuidad, plan_director_seguridad, politica_seguridad_informacion, plan_continuidad. La obligación queda sin soporte documental.

- Dominio: Banxico / IFPE
- Requisito: Las IFPE se sujetan a las disposiciones conjuntas Banxico-CNBV del 28 de enero de 2021 en seguridad de la información, registro de cuentas, medios electrónicos y continuidad operativa. La política y los planes los aprueba el órgano de administración.
- Corrección sugerida: Apruebe por el órgano de administración la política de continuidad y el plan de seguridad exigidos por las disposiciones conjuntas Banxico-CNBV del 28 de enero de 2021.
- Fuente: [Disposiciones IFPE Banxico-CNBV DOF 28-ene-2021](https://dof.gob.mx/nota_detalle.php?codigo=5610487&fecha=28/01/2021) · vigencia 2021-01-28 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · critical · `condusef-consentimiento-expreso`

**Consentimiento expreso — prohibido el tácito en contratos**

Se revisó contrato_adhesion.md, terminos_plataforma.md. No coincide la forma de consentimiento expreso. Se encontró un consentimiento tácito o la aceptación al continuar navegando.

- Dominio: CONDUSEF
- Requisito: La formalización usa firma electrónica avanzada, firma autógrafa digitalizada u otra autenticación del art. 56 de la LRITF. El consentimiento tácito está prohibido.
- Documento: `contrato_adhesion.md`
- Evidencia: “…ectrónico de Nube Pago, S.A. de C.V., IFPE imaginaria. El usuario acepta este contrato al continuar navegando en la plataforma o al mantener la cuenta abierta. Se considera suficiente el consentimien…”
- Corrección sugerida: Elimine la aceptación por seguir navegando o por consentimiento tácito, y describa la firma electrónica, la firma autógrafa digitalizada o la autenticación del art. 56 de la LRITF.
- Fuente: [Disposiciones CONDUSEF ITF art. 8](https://sidof.segob.gob.mx/notas/docFuente/5565233) · vigencia 2019-06-28 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · critical · `condusef-reca-inscripcion-previa`

**Inscripción RECA previa al uso de contratos de adhesión**

Se revisó caratula_cuenta.md, contrato_adhesion.md. No coincide un número de inscripción RECA. Se encontró una inscripción RECA pendiente.

- Dominio: CONDUSEF
- Requisito: Inscribir en el RECA, antes de usarlos, todos los modelos de contratos de adhesión y sus anexos. El contrato y la carátula deben señalar el número de inscripción vigente y completo.
- Documento: `contrato_adhesion.md`
- Evidencia: “…mantener la cuenta abierta. Se considera suficiente el consentimiento tácito. Inscripción RECA: inscripción pendiente. No se imprime un número de registro. No se publican aquí los datos del área que atiende…”
- Corrección sugerida: Inscriba el contrato en el RECA antes de usarlo e imprima el número completo y vigente en el contrato y en la carátula. Quite la leyenda de inscripción pendiente.
- Fuente: [Disposiciones CONDUSEF ITF arts. 31–32](https://sidof.segob.gob.mx/notas/docFuente/5565233) · vigencia 2019-06-28 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · critical · `lritf-continuidad-controles`

**Controles internos, continuidad operativa y seguridad**

No se encontró ningún documento clasificado como: plan_continuidad, manual_control_interno, politica_seguridad_informacion. La obligación queda sin soporte documental.

- Dominio: LRITF
- Requisito: Las ITF se sujetan a disposiciones de carácter general en controles internos, administración de riesgos, segregación de funciones, continuidad operativa y seguridad de la información. Para IFPE, las disposiciones son conjuntas de CNBV y Banxico.
- Corrección sugerida: Documente el plan de continuidad operativa y el manual de control interno, con la aprobación del órgano de administración.
- Fuente: [LRITF art. 48](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf) · vigencia 2018-03-09 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · critical · `lritf-no-garantia-gobierno`

**Divulgación: el Gobierno Federal no garantiza los recursos de los clientes**

Se revisó caratula_cuenta.md, contrato_adhesion.md, publicidad_campana.pdf, terminos_plataforma.md. No aparece la leyenda de no garantía del Gobierno Federal. Se buscó alguna de: «gobierno federal no», «no se encuentran garantizados», «ni las entidades paraestatales», «no garantiza los recursos», «no podrán responsabilizarse», «no podran responsabilizarse», «no están garantizados por el gobierno», «no estan garantizados por el gobierno», «no garantiza ni se responsabiliza».

- Dominio: LRITF
- Requisito: Las ITF deben señalar expresamente que el Gobierno Federal y las entidades paraestatales no pueden responsabilizarse ni garantizar los recursos de los clientes, en páginas, aplicaciones, publicidad y contratos.
- Documento: `caratula_cuenta.md`
- Evidencia: “DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. No corresponde a ninguna entidad autorizada. # Carátula del producto Producto: cuenta de pago. Precio…”
- Corrección sugerida: Inserte en el contrato, la carátula, la publicidad y los términos la leyenda de que el Gobierno Federal y las entidades paraestatales no garantizan ni se responsabilizan de los recursos de los clientes.
- Fuente: [LRITF art. 11](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf) · vigencia 2018-03-09 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · critical · `lritf-politicas-segregacion`

**Políticas de separación o segregación de cuentas de clientes**

No se encontró ningún documento clasificado como: politica_segregacion, manual_operaciones, politica_tesoreria. La obligación queda sin soporte documental.

- Dominio: LRITF
- Requisito: La operación exige políticas de separación de cuentas: los recursos de clientes se segregan de los propios y se depositan conforme al art. 46.
- Corrección sugerida: Documente la segregación: cuentas distintas de las propias, depósito de los recursos de clientes y el momento en que se realiza.
- Fuente: [LRITF arts. 39-IV, 46](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf) · vigencia 2018-03-09 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · critical · `lritf-seguridad-informacion`

**Políticas de control de riesgos operativos y seguridad de la información**

No se encontró ningún documento clasificado como: politica_seguridad_informacion, manual_riesgos_operativos, politica_confidencialidad. La obligación queda sin soporte documental.

- Dominio: LRITF
- Requisito: Medidas y políticas de riesgos operativos y seguridad de la información, incluida la confidencialidad, con soporte tecnológico y estándares de confidencialidad, disponibilidad e integridad.
- Corrección sugerida: Apruebe una política de seguridad de la información que cubra confidencialidad, disponibilidad e integridad, y el control de riesgos operativos.
- Fuente: [LRITF art. 39-VI](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf) · vigencia 2018-03-09 · verificado 2026-11-05
- Origen: deterministic

### Cumple · critical · `pld-kyc-identificacion`

**Conocimiento e identificación de clientes**

Los documentos revisados cubren el criterio: manual_pld_ft.md, procedimiento_kyc.txt.

- Dominio: PLD/FT
- Requisito: Definir criterios de conocimiento del cliente (antecedentes, actividad, zonas) y la información y documentación que acredite la identidad, con resguardo seguro.
- Documento: `manual_pld_ft.md`
- Corrección sugerida: Documente, por tipo de cliente, la identificación exigida, la actividad y la zona, y el resguardo del expediente.
- Fuente: [LRITF art. 58 (lineamientos de conocimiento del cliente)](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf) · vigencia 2018-09-10 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · critical · `pld-lista-bloqueados`

**Suspensión inmediata por lista de personas bloqueadas**

Se revisó manual_pld_ft.md. No aparece la lista de personas bloqueadas. Se buscó alguna de: «personas bloqueadas», «lista de personas bloqueadas», «lista de bloqueados».

- Dominio: PLD/FT
- Requisito: Suspender de forma inmediata los actos, operaciones o servicios con clientes que figuren en la lista de personas bloqueadas que informe la Secretaría.
- Documento: `manual_pld_ft.md`
- Evidencia: “DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. No corresponde a ninguna entidad autorizada. # Manual PLD/FT — borrador interno Versión 0.2. Fecha de…”
- Corrección sugerida: Documente la consulta de la lista de personas bloqueadas y la suspensión inmediata de operaciones cuando haya coincidencia.
- Fuente: [LRITF art. 58](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf) · vigencia 2018-09-10 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · critical · `pld-manual-art58`

**Manual de medidas y procedimientos PLD/FT (art. 58)**

Se revisó manual_pld_ft.md. No aparece el fundamento del artículo 58. Se buscó alguna de: «artículo 58», «articulo 58», «art. 58». Se encontró un manual no presentado a la autoridad: «no ha sido presentado».

- Dominio: PLD/FT
- Requisito: Las medidas y procedimientos para prevenir y detectar actos de los arts. 139 Quáter o 400 Bis del Código Penal Federal deben constar en un documento presentado a la CNBV conforme a las DCG del art. 58.
- Documento: `manual_pld_ft.md`
- Evidencia: “…Fecha de redacción: enero de 2023. Entidad ficticia Nube Pago, S.A. de C.V. Este borrador no ha sido presentado a la CNBV. Alcance: cuenta de dinero electrónico de la entidad ficticia. El documento no…”
- Corrección sugerida: Cierre una versión del manual PLD/FT con fundamento en el art. 58 de la LRITF y regístrela como presentada a la CNBV, con fecha y alcance de productos.
- Fuente: [LRITF art. 58-I; DCG SIDOF 5537449](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf) · vigencia 2018-09-10 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · critical · `pld-metodologia-riesgos`

**Metodología de evaluación de riesgos PLD/FT**

Se revisó manual_pld_ft.md. No aparece la metodología de riesgos PLD/FT. Se buscó alguna de: «enfoque basado en riesgos», «enfoque basado en riesgo», «metodología de riesgos», «metodologia de riesgos», «evaluación de riesgos», «evaluacion de riesgos», «metodología de evaluación».

- Dominio: PLD/FT
- Requisito: Diseñar e implementar una metodología de evaluación de riesgos por productos, servicios, prácticas o tecnologías, con resultados a disposición de la Secretaría y de la CNBV.
- Documento: `manual_pld_ft.md`
- Evidencia: “DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. No corresponde a ninguna entidad autorizada. # Manual PLD/FT — borrador interno Versión 0.2. Fecha de…”
- Corrección sugerida: Documente la metodología de evaluación de riesgos (enfoque basado en riesgos) por producto, cliente, zona y canal, y conserve los resultados.
- Fuente: [LRITF art. 58-I](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf) · vigencia 2018-09-10 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · critical · `pld-oficial-cumplimiento-certificado`

**Oficial de cumplimiento y comité de comunicación y control**

Se revisó manual_pld_ft.md, nombramiento_oficial_cumplimiento.docx. Faltan elementos: Comité de comunicación y control. Se encontró un oficial vacante o sin certificación: «vacante».

- Dominio: PLD/FT
- Requisito: Debe existir un comité de comunicación y control y un oficial de cumplimiento. El oficial y quien haga la revisión anual deben obtener la certificación del art. 4 fr. X de la Ley de la CNBV.
- Documento: `nombramiento_oficial_cumplimiento.docx`
- Evidencia: “…izada. Nombramiento del oficial de cumplimiento El puesto de oficial de cumplimiento está vacante. La entidad ficticia no cuenta con certificación CNBV para ese puesto. Puesto | Estado Of…”
- Corrección sugerida: Designe al oficial de cumplimiento y al comité, y conserve la constancia de certificación CNBV del oficial y del revisor anual. Un puesto vacante no sustituye el nombramiento.
- Fuente: [LRITF art. 58](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf) · vigencia 2018-09-10 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · critical · `pld-reportes-roi-ror-rop`

**Reportes de operaciones relevantes, inusuales e internas preocupantes**

Se revisó manual_pld_ft.md. Faltan elementos: Operaciones relevantes; Operaciones inusuales; Operaciones internas preocupantes.

- Dominio: PLD/FT
- Requisito: Presentar a la Secretaría, por conducto de la CNBV, reportes que cubran al menos operaciones relevantes, internas preocupantes e inusuales, además de transferencias internacionales y efectivo en moneda extranjera, conforme a las DCG.
- Documento: `manual_pld_ft.md`
- Evidencia: “DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. No corresponde a ninguna entidad autorizada. # Manual PLD/FT — borrador interno Versión 0.2. Fecha de…”
- Corrección sugerida: Describa la dictaminación y el envío, vía CNBV, de operaciones relevantes, inusuales e internas preocupantes, con los plazos de cada una.
- Fuente: [LRITF art. 58-II](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf) · vigencia 2018-09-10 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · critical · `privacy-aviso-art15-elementos`

**Aviso de privacidad — elementos mínimos art. 15 LFPDPPP 2025**

Se revisó aviso_de_privacidad.md. Faltan elementos: III. Finalidades que distinguen las que requieren consentimiento; VI. Medio para comunicar cambios al aviso.

- Dominio: Datos personales (LFPDPPP)
- Requisito: El aviso debe contener al menos: (I) identidad y domicilio del responsable; (II) datos personales tratados, identificando sensibles; (III) finalidades, distinguiendo las que requieren consentimiento; (IV) opciones/medios para limitar uso o divulgación; (V) mecanismos ARCO; (VI) procedimiento y medio para comunicar cambios al aviso.
- Documento: `aviso_de_privacidad.md`
- Evidencia: “DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. No corresponde a ninguna entidad autorizada. # Aviso de privacidad Responsable del tratamiento: Nube …”
- Corrección sugerida: Reescriba el aviso con seis apartados explícitos. En finalidades separe las que requieren consentimiento de las que no, y agregue cómo se comunicarán los cambios al aviso.
- Fuente: [LFPDPPP art. 15 (DOF 20-mar-2025)](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf) · vigencia 2025-03-21 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · high · `condusef-caratula-leyendas`

**Carátula con leyendas de advertencia**

Se revisó caratula_cuenta.md. Faltan elementos: Leyenda de no garantía; Aclaración de rendimientos.

- Dominio: CONDUSEF
- Requisito: Cada producto lleva carátula con el formato de los anexos y las leyendas aplicables: recursos no garantizados, rendimientos estimados cuando existan, y, para IFPE, la aclaración sobre rendimientos.
- Documento: `caratula_cuenta.md`
- Evidencia: “DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. No corresponde a ninguna entidad autorizada. # Carátula del producto Producto: cuenta de pago. Precio…”
- Corrección sugerida: Arme la carátula con la leyenda de recursos no garantizados por el Gobierno Federal y la aclaración de rendimientos que corresponda al producto.
- Fuente: [Disposiciones CONDUSEF ITF art. 7](https://sidof.segob.gob.mx/notas/docFuente/5565233) · vigencia 2019-06-28 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · high · `condusef-reus-publicidad`

**REUS y consentimiento independiente para publicidad**

Se revisó contrato_adhesion.md. No aparece el REUS. Se buscó alguna de: «REUS». No aparece el consentimiento de publicidad separado del contrato. Se buscó alguna de: «consentimiento independiente», «autorización expresa para publicidad», «autorizacion expresa para publicidad», «consentimiento para publicidad», «consentimiento de publicidad».

- Dominio: CONDUSEF
- Requisito: La publicidad requiere autorización expresa e independiente del contrato. No se usa información de usuarios inscritos en el REUS salvo autorización posterior a esa inscripción.
- Documento: `contrato_adhesion.md`
- Evidencia: “DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. No corresponde a ninguna entidad autorizada. # Contrato de adhesión Producto: cuenta de dinero electr…”
- Corrección sugerida: Documente la consulta al REUS antes de enviar publicidad y separe el consentimiento publicitario de la aceptación del contrato.
- Fuente: [Disposiciones CONDUSEF ITF art. 11](https://sidof.segob.gob.mx/notas/docFuente/5565233) · vigencia 2019-06-28 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · high · `condusef-une`

**UNE — datos de contacto en el contrato y en la plataforma**

Se revisó caratula_cuenta.md, contrato_adhesion.md, terminos_plataforma.md. No coincide la Unidad Especializada de atención a usuarios.

- Dominio: CONDUSEF
- Requisito: El contrato debe incluir los datos de la Unidad Especializada (correo y, en su caso, teléfono) para consultas, reclamaciones y aclaraciones. La plataforma también.
- Documento: `caratula_cuenta.md`
- Evidencia: “DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. No corresponde a ninguna entidad autorizada. # Carátula del producto Producto: cuenta de pago. Precio…”
- Corrección sugerida: Agregue en el contrato y en la plataforma el nombre de la Unidad Especializada, su correo y, si existe, el teléfono.
- Fuente: [Disposiciones CONDUSEF ITF art. 6-VII](https://sidof.segob.gob.mx/notas/docFuente/5565233) · vigencia 2019-06-28 · verificado 2026-11-05
- Origen: deterministic

### No aplica · high · `lritf-av-divulgacion-riesgos`

**Divulgación de riesgos de activos virtuales**

No aplica con el perfil actual: no se declaró `operates_virtual_assets`. Actívelo en la CLI o en la interfaz si el modelo de negocio entra en el supuesto.

- Dominio: LRITF
- Requisito: Quien opere con activos virtuales debe divulgar que no son moneda de curso legal ni están respaldados por el Gobierno o Banxico, y advertir irreversibilidad, volatilidad y riesgos tecnológicos, cibernéticos y de fraude.
- Corrección sugerida: Si opera activos virtuales, agregue en carátula y plataforma que no son moneda de curso legal ni están respaldados por el Gobierno Federal o Banxico, y advierta volatilidad e irreversibilidad.
- Fuente: [LRITF art. 34](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf) · vigencia 2018-03-09 · verificado 2026-11-05
- Origen: deterministic

### Cumple · high · `lritf-conflictos-interes`

**Políticas de solución de conflictos de interés**

Los documentos revisados cubren el criterio: politica_conflictos_interes.md.

- Dominio: LRITF
- Requisito: Políticas documentadas para los posibles conflictos de interés en la realización de las actividades.
- Documento: `politica_conflictos_interes.md`
- Corrección sugerida: Documente cómo se revelan, registran y resuelven los conflictos de interés, incluida la abstención de quien los tenga.
- Fuente: [LRITF art. 39-VIII](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf) · vigencia 2018-03-09 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · high · `lritf-divulgacion-riesgos-comisiones`

**Políticas de divulgación de riesgos, responsabilidades y comisiones**

Se revisó terminos_plataforma.md. Faltan elementos: Riesgos del producto; Comisiones.

- Dominio: LRITF
- Requisito: Políticas en lenguaje sencillo sobre riesgos, responsabilidades, conceptos y montos de comisiones, y advertencias en la interfaz.
- Documento: `terminos_plataforma.md`
- Evidencia: “DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. No corresponde a ninguna entidad autorizada. # Términos y condiciones de la plataforma El uso de la p…”
- Corrección sugerida: Publique, en lenguaje sencillo, los riesgos del producto y el concepto, monto y periodicidad de cada comisión antes de que el cliente opere.
- Fuente: [LRITF art. 39-V](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf) · vigencia 2018-03-09 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · high · `lritf-prevencion-fraude`

**Políticas de prevención de fraudes**

No se encontró ningún documento clasificado como: politica_prevencion_fraude, manual_operaciones. La obligación queda sin soporte documental.

- Dominio: LRITF
- Requisito: Políticas de prevención de fraudes, además de las de PLD/FT.
- Corrección sugerida: Separe una política de prevención de fraudes, con señales de alerta, responsables y el escalamiento operativo.
- Fuente: [LRITF art. 39-IX](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf) · vigencia 2018-03-09 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · high · `lfpiorpi-2025-manual-rba-av`

**Reforma LFPIORPI 2025 — beneficiario controlador, UMA y manual**

Se revisó manual_pld_ft.md. Faltan elementos: Beneficiario controlador; Reforma o actividades vulnerables; UMA o monitoreo automatizado.

- Dominio: PLD/FT
- Requisito: La reforma publicada el 16 de julio de 2025 redefine al beneficiario controlador, sustituye umbrales por UMA, exige identificación directa, manual de políticas, enfoque basado en riesgos, monitoreo automatizado, capacitación y auditoría, y conserva la información diez años. Es relevante para quien intercambie activos virtuales fuera de una entidad financiera y como contexto de las entidades del art. 58 de la LRITF.
- Documento: `manual_pld_ft.md`
- Evidencia: “DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. No corresponde a ninguna entidad autorizada. # Manual PLD/FT — borrador interno Versión 0.2. Fecha de…”
- Corrección sugerida: Actualice el manual con la reforma del 16 de julio de 2025: beneficiario controlador, umbrales en UMA, monitoreo automatizado y el régimen de actividades vulnerables si la entidad o una filial entra en ese supuesto.
- Fuente: [LFPIORPI reforma DOF 16-jul-2025](https://www.diputados.gob.mx/LeyesBiblio/ref/lfpiorpi/LFPIORPI_ref03_16jul25.pdf) · vigencia 2025-07-17 · verificado 2026-11-05
- Nota: Las fracciones VII a XI del art. 18 entran según las reglas secundarias (transitorio tercero). No se adelantan aquí plazos que el decreto condiciona.
- Origen: deterministic

### Incumplimiento · high · `pld-auditoria-anual`

**Revisión anual de la efectividad PLD/FT**

No se encontró ningún documento clasificado como: informe_auditoria_pld. La obligación queda sin soporte documental.

- Dominio: PLD/FT
- Requisito: Revisión anual, por auditoría interna o por un tercero independiente, de la efectividad del cumplimiento de las DCG del art. 58.
- Corrección sugerida: Encargue y archive el informe anual de efectividad PLD/FT, emitido por auditoría interna o por un tercero independiente certificado.
- Fuente: [LRITF art. 58; lineamientos CNBV 18-oct-2021 (índice Normatividad Fintech)](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf) · vigencia 2018-09-10 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · high · `pld-retencion-10-anos`

**Conservación de expedientes KYC y reportes PLD por al menos 10 años**

Se revisó manual_pld_ft.md. No aparece la conservación de diez años. Se buscó alguna de: «diez años», «10 años», «10 (diez) años».

- Dominio: PLD/FT
- Requisito: Conservar al menos diez años la información y documentación de identificación de clientes y de los actos u operaciones reportados.
- Documento: `manual_pld_ft.md`
- Evidencia: “DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. No corresponde a ninguna entidad autorizada. # Manual PLD/FT — borrador interno Versión 0.2. Fecha de…”
- Corrección sugerida: Corrija el plazo de conservación de expedientes de identificación y de reportes PLD a un mínimo de diez años.
- Fuente: [LRITF art. 58](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf) · vigencia 2018-09-10 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · high · `privacy-aviso-vulneraciones`

**Aviso inmediato de vulneraciones significativas a titulares**

No se encontró ningún documento clasificado como: plan_respuesta_incidentes, politica_seguridad_datos. La obligación queda sin soporte documental.

- Dominio: Datos personales (LFPDPPP)
- Requisito: Las vulneraciones que afecten de forma significativa derechos patrimoniales o morales deben informarse de forma inmediata a los titulares.
- Corrección sugerida: Agregue al plan de incidentes el aviso inmediato a los titulares cuando la vulneración afecte de forma significativa sus derechos.
- Fuente: [LFPDPPP art. 19](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf) · vigencia 2025-03-21 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · high · `privacy-consentimiento-datos-financieros`

**Consentimiento expreso para datos financieros o patrimoniales**

Se revisó aviso_de_privacidad.md. Faltan elementos: Consentimiento expreso de datos financieros o patrimoniales. Se encontró un consentimiento tácito para datos personales: «de forma tácita».

- Dominio: Datos personales (LFPDPPP)
- Requisito: Los datos financieros o patrimoniales requieren consentimiento expreso del titular, salvo excepciones de los arts. 9 y 36.
- Documento: `aviso_de_privacidad.md`
- Evidencia: “…otección de Datos Personales). El tratamiento de datos financieros se entiende consentido de forma tácita al abrir la cuenta.”
- Corrección sugerida: Redacte que los datos financieros o patrimoniales se tratan con consentimiento expreso del titular y elimine cualquier fórmula de consentimiento tácito.
- Fuente: [LFPDPPP art. 7](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf) · vigencia 2025-03-21 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · high · `privacy-medidas-seguridad`

**Medidas de seguridad administrativas, técnicas y físicas**

No se encontró ningún documento clasificado como: politica_seguridad_datos, politica_seguridad_informacion. La obligación queda sin soporte documental.

- Dominio: Datos personales (LFPDPPP)
- Requisito: Deben establecerse y mantenerse medidas que protejan los datos contra daño, pérdida, alteración, destrucción o uso y acceso no autorizados.
- Corrección sugerida: Documente medidas administrativas, técnicas y físicas de seguridad de los datos personales, alineadas al art. 18 de la LFPDPPP.
- Fuente: [LFPDPPP art. 18](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf) · vigencia 2025-03-21 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · high · `privacy-no-citar-inai`

**No citar al INAI como autoridad vigente**

Se revisó aviso_de_privacidad.md. Se encontró al INAI o al Instituto Nacional de Transparencia como autoridad vigente: «INAI».

- Dominio: Datos personales (LFPDPPP)
- Requisito: Tras la LFPDPPP 2025, la autoridad es la Secretaría Anticorrupción y Buen Gobierno. Documentos que indiquen al INAI como autoridad garante vigente están desactualizados.
- Documento: `aviso_de_privacidad.md`
- Evidencia: “…s: privacidad@nubepago.example. La autoridad competente para la protección de datos es el INAI (Instituto Nacional de Transparencia, Acceso a la Información y Protección de Datos Perso…”
- Corrección sugerida: Sustituya toda referencia al INAI como autoridad vigente por la Secretaría Anticorrupción y Buen Gobierno y cite la LFPDPPP publicada el 20 de marzo de 2025.
- Fuente: [LFPDPPP arts. 2-XV, 38–39; Transitorios DOF 20-mar-2025](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf) · vigencia 2025-03-21 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · high · **UNVERIFIED** · `sat-cfdi40-emision`

**Proceso documentado de emisión de CFDI 4.0**

Se revisó politica_cfdi.md. No aparece CFDI versión 4.0. Se buscó alguna de: «CFDI 4.0», «versión 4.0», «version 4.0», «cfdi version 4.0».

- Dominio: SAT / fiscal
- Requisito: Contar con un procedimiento de facturación electrónica CFDI 4.0 alineado al CFF, a la RMF 2026 y al Anexo 29, incluidas las cancelaciones y las validaciones.
- Documento: `politica_cfdi.md`
- Evidencia: “DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. No corresponde a ninguna entidad autorizada. # Política de facturación Nos regimos únicamente por la …”
- Corrección sugerida: Migre el procedimiento de CFDI 3.3 a CFDI 4.0 y documente timbrado, cancelación y validaciones. Confirme los números de regla contra el PDF de la RMF 2026 antes de citarlos.
- Fuente: [SAT RMF 2026 / Anexo 29 (hub)](https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/normatividad_rmf_rgce2026.html) · vigencia 2022-01-01 · verificado 2026-11-05
- UNVERIFIED: Los números de regla de la RMF 2026 que detallan el CFDI no se transcribieron: el PDF completo no se leyó línea por línea. La versión 4.0 sí es el estándar vigente que el procedimiento debe nombrar.
- Origen: deterministic

### No aplica · high · `sat-plataformas-tecnologicas`

**Retenciones y complemento de plataformas tecnológicas**

No aplica con el perfil actual: no se declaró `is_technological_platform_tax_regime`. Actívelo en la CLI o en la interfaz si el modelo de negocio entra en el supuesto.

- Dominio: SAT / fiscal
- Requisito: Si la entidad es plataforma tecnológica en los supuestos de la LISR o de la LIVA, debe documentar el CFDI de retenciones con el complemento de servicios de plataformas tecnológicas y los enteros.
- Corrección sugerida: Si está en el régimen de plataformas tecnológicas, documente el complemento y el entero de las retenciones. Si no lo está, no active la bandera.
- Fuente: [SAT Complemento Servicios de Plataformas Tecnológicas](https://wwwmat.sat.gob.mx/consulta/52846/complemento-servicios-de-plataformas-tecnologicas) · vigencia 2019-06-01 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · high · `sat-rmf-calendario-anual`

**Calendario de actualización ante la RMF anual**

Se revisó politica_cfdi.md. Faltan elementos: Calendario o lista de verificación; Persona responsable.

- Dominio: SAT / fiscal
- Requisito: La Resolución Miscelánea Fiscal se publica cada año. Los procesos fiscales deben tener una persona responsable y una lista de verificación después de la publicación en el DOF, más el seguimiento de las resoluciones de modificaciones.
- Documento: `politica_cfdi.md`
- Evidencia: “DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. No corresponde a ninguna entidad autorizada. # Política de facturación Nos regimos únicamente por la …”
- Corrección sugerida: Nombre a la persona responsable y arme la lista de verificación que se corre al publicarse la RMF 2026 y cada resolución de modificaciones.
- Fuente: [SAT Normatividad RMF 2026; RMF publicada el 28-dic-2025](https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/normatividad_rmf_rgce2026.html) · vigencia 2026-01-01 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · high · `sat-rmf2026-publicacion`

**Referenciar la RMF 2026 vigente**

Se revisó politica_cfdi.md. No aparece la RMF 2026. Se buscó alguna de: «RMF 2026», «miscelánea fiscal 2026», «miscelanea fiscal 2026», «resolución miscelánea fiscal para 2026», «resolucion miscelanea fiscal para 2026».

- Dominio: SAT / fiscal
- Requisito: Las políticas y los manuales fiscales no deben quedar anclados solo a la RMF 2025. Deben citar o incorporar la RMF 2026 y las modificaciones publicadas.
- Documento: `politica_cfdi.md`
- Evidencia: “DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. No corresponde a ninguna entidad autorizada. # Política de facturación Nos regimos únicamente por la …”
- Corrección sugerida: Actualice la cita normativa a la Resolución Miscelánea Fiscal 2026 y deje constancia de la revisión de sus modificaciones.
- Fuente: [RMF 2026 DOF 28-dic-2025](https://dof.gob.mx/2025/SHCP/SHCP_281225_01.pdf) · vigencia 2026-01-01 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · medium · `condusef-comisiones-plataforma`

**Comisiones publicadas antes de operar**

Se revisó contrato_adhesion.md. Faltan elementos: Comisiones; Monto o periodicidad.

- Dominio: CONDUSEF
- Requisito: Los conceptos, montos y la periodicidad de las comisiones deben estar disponibles antes de operar, con consentimiento previo al cobro.
- Documento: `contrato_adhesion.md`
- Evidencia: “DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. No corresponde a ninguna entidad autorizada. # Contrato de adhesión Producto: cuenta de dinero electr…”
- Corrección sugerida: Publique concepto, monto y periodicidad de cada comisión, y recabe el consentimiento del cliente antes de cobrarla.
- Fuente: [Disposiciones CONDUSEF ITF arts. 33–34](https://sidof.segob.gob.mx/notas/docFuente/5565233) · vigencia 2019-06-28 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · medium · `condusef-terminos-plataforma`

**Términos y condiciones de uso de la plataforma**

Se revisó terminos_plataforma.md. Faltan elementos: Claves, robo o extravío; Aviso a CONDUSEF por fallas prolongadas.

- Dominio: CONDUSEF
- Requisito: Los términos explican usos y restricciones, la responsabilidad sobre claves y el procedimiento por robo, extravío u olvido, los horarios, los medios de continuidad ante fallas y el aviso a CONDUSEF cuando una falla dure 24 horas o más.
- Documento: `terminos_plataforma.md`
- Evidencia: “DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. No corresponde a ninguna entidad autorizada. # Términos y condiciones de la plataforma El uso de la p…”
- Corrección sugerida: Complete los términos con el uso de claves y el procedimiento por robo o extravío, los horarios, la continuidad ante fallas y el aviso a CONDUSEF (suptech@condusef.gob.mx) si la falla dura 24 horas o más.
- Fuente: [Disposiciones CONDUSEF ITF art. 3](https://sidof.segob.gob.mx/notas/docFuente/5565233) · vigencia 2019-06-28 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · medium · `lritf-conservacion-10-anos`

**Conservación de comprobantes de operaciones por al menos 10 años**

No se encontró ningún documento clasificado como: politica_retencion_documental, manual_archivo. La obligación queda sin soporte documental.

- Dominio: LRITF
- Requisito: Conservar los comprobantes originales de las operaciones por un plazo mínimo de diez años, en impreso o en medios electrónicos conforme a la NOM de digitalización.
- Corrección sugerida: Fije en la política de archivo un plazo mínimo de diez años para los comprobantes de las operaciones.
- Fuente: [LRITF art. 48](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf) · vigencia 2018-03-09 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · medium · `pld-dcg-art58-fuente`

**Anclar los controles a las DCG del art. 58**

Se revisó manual_pld_ft.md. Faltan elementos: Artículo 58; Disposiciones de carácter general.

- Dominio: PLD/FT
- Requisito: El manual debe alinearse a las Disposiciones de carácter general del artículo 58 de la LRITF, publicadas el 10 de septiembre de 2018, y a sus modificaciones.
- Documento: `manual_pld_ft.md`
- Evidencia: “DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. No corresponde a ninguna entidad autorizada. # Manual PLD/FT — borrador interno Versión 0.2. Fecha de…”
- Corrección sugerida: Cite en el manual las DCG del art. 58 de la LRITF (SIDOF 5537449, 10 de septiembre de 2018) y las modificaciones que les apliquen.
- Fuente: [DCG art. 58 LRITF (10-sep-2018)](https://sidof.segob.gob.mx/notas/5537449) · vigencia 2018-09-10 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · medium · `privacy-arco-plazos`

**Procedimiento ARCO — plazos de respuesta**

Se revisó aviso_de_privacidad.md. No coincide el plazo máximo de 20 días. No coincide el plazo de 15 días para hacer efectivo el derecho.

- Dominio: Datos personales (LFPDPPP)
- Requisito: El responsable debe comunicar la determinación en máximo 20 días desde la solicitud y, si procede, hacerla efectiva en los 15 días siguientes, ampliables una vez por igual periodo.
- Documento: `aviso_de_privacidad.md`
- Evidencia: “DOCUMENTO FICTICIO DE DEMOSTRACIÓN — Nube Pago, S.A. de C.V., IFPE imaginaria. No corresponde a ninguna entidad autorizada. # Aviso de privacidad Responsable del tratamiento: Nube …”
- Corrección sugerida: Escriba los plazos del art. 31: respuesta en un máximo de 20 días y, de ser procedente, hacerla efectiva dentro de los 15 días siguientes.
- Fuente: [LFPDPPP art. 31](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf) · vigencia 2025-03-21 · verificado 2026-11-05
- Origen: deterministic

### Cumple · medium · `privacy-departamento-datos`

**Designación de persona o departamento de datos personales**

Los documentos revisados cubren el criterio: aviso_de_privacidad.md.

- Dominio: Datos personales (LFPDPPP)
- Requisito: Todo responsable debe designar una persona o departamento que tramite las solicitudes ARCO.
- Documento: `aviso_de_privacidad.md`
- Corrección sugerida: Nombre el departamento o la persona que atiende ARCO y publique un correo de contacto en el aviso.
- Fuente: [LFPDPPP art. 29](https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf) · vigencia 2025-03-21 · verificado 2026-11-05
- Origen: deterministic

### No aplica · medium · `sat-carta-porte`

**Complemento Carta Porte si hay transporte de mercancías**

No aplica con el perfil actual: no se declaró `transports_goods`. Actívelo en la CLI o en la interfaz si el modelo de negocio entra en el supuesto.

- Dominio: SAT / fiscal
- Requisito: Solo si la fintech, o un tercero cubierto por su CFDI, mueve mercancías en territorio nacional, debe emitirse el complemento Carta Porte.
- Corrección sugerida: Si transporta mercancías, documente el complemento Carta Porte. Si no transporta, deje constancia de que el supuesto no aplica y no active esta bandera.
- Fuente: [SAT Complemento Carta Porte](https://wwwmat.sat.gob.mx/consultas/68823/complemento-carta-porte-) · vigencia 2021-12-01 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · medium · **UNVERIFIED** · `sat-cff-32b-informacion`

**CFF art. 32-B — información de entidades financieras**

No se encontró ningún documento clasificado como: procedimiento_requerimientos_autoridad, manual_fiscal. La obligación queda sin soporte documental.

- Dominio: SAT / fiscal
- Requisito: Si la entidad queda en los supuestos del art. 32-B del CFF, debe poder atender requerimientos del SAT sobre cuentas y operaciones e identificar cuentahabientes.
- Corrección sugerida: Documente quién atiende un requerimiento del SAT y qué datos de identificación se pueden entregar. Confirme contra el CFF vigente si la entidad está en el supuesto del art. 32-B.
- Fuente: [CFF art. 32-B (cruzar con el CFF vigente en Diputados); la ficha de investigación citó la LRITF solo como ancla](https://www.diputados.gob.mx/LeyesBiblio/pdf/LRITF.pdf) · vigencia 2014-01-01 · verificado 2026-11-05
- UNVERIFIED: El encuadre exacto de cada ITF en el art. 32-B del CFF no se cerró contra el texto vigente del CFF. La URL de esta ficha es la que traía la semilla de investigación (compilación de la LRITF) y debe cruzarse con el PDF del CFF.
- Origen: deterministic

### No aplica · medium · **UNVERIFIED** · `sat-complemento-pagos-rep`

**Complemento de recepción de pagos**

No aplica con el perfil actual: no se declaró `has_partial_or_deferred_payments`. Actívelo en la CLI o en la interfaz si el modelo de negocio entra en el supuesto.

- Dominio: SAT / fiscal
- Requisito: Si se reciben pagos en parcialidades o diferidos, debe documentarse la emisión del complemento de recepción de pagos conforme a las reglas vigentes.
- Corrección sugerida: Si hay pagos parciales o diferidos, documente quién emite el complemento de recepción de pagos y en qué momento. Confirme el plazo en la regla vigente de la RMF 2026.
- Fuente: [SAT RMF 2026 (hub), complemento de pagos](https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/normatividad_rmf_rgce2026.html) · vigencia 2022-01-01 · verificado 2026-11-05
- UNVERIFIED: El plazo coloquialmente citado como quinto día del mes siguiente debe confirmarse en la regla vigente de la RMF 2026; no se copia un número de regla no leído.
- Origen: deterministic

### No aplica · medium · `sat-iva-servicios-digitales`

**IVA de servicios digitales — comprobantes**

No aplica con el perfil actual: no se declaró `provides_digital_services_liva`. Actívelo en la CLI o en la interfaz si el modelo de negocio entra en el supuesto.

- Dominio: SAT / fiscal
- Requisito: Quien preste servicios digitales en los supuestos de la LIVA debe documentar el traslado del IVA, el RFC del receptor y los datos del emisor en los comprobantes.
- Corrección sugerida: Si presta servicios digitales gravados, documente el IVA y los datos del comprobante según la guía del SAT. Si no, no active la bandera.
- Fuente: [SAT Plataformas Tecnológicas / Servicios Digitales — comprobantes](https://www.sat.gob.mx/minisitio/PlataformasTecnologicas/PlataformasTecnologicas_ServiciosDigitales/pt_sd_comprobantes.html) · vigencia 2020-06-01 · verificado 2026-11-05
- Origen: deterministic

### Incumplimiento · info · `cnbv-normatividad-index`

**Mantener el mapeo a la Normatividad Fintech de la CNBV**

No se encontró ningún documento clasificado como: matriz_cumplimiento, manual_cumplimiento. La obligación queda sin soporte documental.

- Dominio: CNBV
- Requisito: El programa de cumplimiento debe referenciar el índice oficial de normatividad ITF de la CNBV.
- Corrección sugerida: Agregue a la matriz de cumplimiento la liga al índice de Normatividad Fintech de la CNBV y la fecha en que se revisó.
- Fuente: [CNBV Normatividad Fintech](https://www.cnbv.gob.mx/SECTORES-SUPERVISADOS/Fintech/Paginas/NORMATIVIDAD-FINTECH.aspx) · vigencia 2018-09-10 · verificado 2026-11-05
- Origen: deterministic

## Reglas no aplicadas

- `meta-disclaimer-no-legal-advice`: Regla interna de la herramienta; no se audita al cliente.
- `meta-what-changed-2026`: Regla interna de la herramienta; no se audita al cliente.
- `sat-lif2026-ifc-retencion-isr-iva`: No aplica a IFPE; la regla está dirigida a IFC.

---

AVISO: Este reporte no es asesoría legal ni fiscal. Es un checklist asistido que cita fuentes públicas con fecha de verificación. Las reglas marcadas UNVERIFIED requieren lectura íntegra del instrumento oficial antes de tratarlas como definitivas. Toda decisión de cumplimiento debe validarse con un abogado o contador autorizado y contra el texto vigente en el Diario Oficial de la Federación y los portales oficiales (SAT, CNBV, Banxico, CONDUSEF, UIF, Cámara de Diputados).
