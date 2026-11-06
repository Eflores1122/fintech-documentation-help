# Nube Pago, S.A. de C.V. — entidad ficticia

Nube Pago no existe, no está autorizada y no corresponde a ningún empleador, cliente o fintech real. Los documentos en `docs/` son sintéticos y traen huecos a propósito para demostrar el auditor.

Audite solo la carpeta `docs/`:

```bash
fdh audit samples/nube_pago/docs --year 2026 --entity IFPE
```

Huecos deliberados, entre otros:

- El aviso cita al INAI, no distingue finalidades que requieren consentimiento, no explica cómo se comunican los cambios y trata datos financieros con consentimiento tácito. Los plazos ARCO dicen 30 días.
- El contrato no tiene número RECA (dice inscripción pendiente), se acepta al continuar navegando y no trae UNE ni leyenda de no garantía del Gobierno Federal.
- La carátula no trae las leyendas de advertencia.
- El manual PLD es un borrador de 2023 no presentado a la CNBV, sin art. 58, sin reportes relevantes/inusuales/preocupantes, sin lista de personas bloqueadas, sin diez años y sin la reforma LFPIORPI 2025. El oficial de cumplimiento está vacante y sin certificación CNBV. No hay informe de auditoría.
- No hay políticas de segregación, fraude ni retención de comprobantes. Hay una política de seguridad delgada (confidencialidad, sin MFA ni cifrado) y un plan de continuidad con RTO «por definir», sin simulacro.
- La política fiscal sigue en la RMF 2025 y en CFDI 3.3. La política contable se ancla a criterios de 2018.
- El capital está «por definir» y cita 100,000 UDI. El plan de incidentes dice «72 horas para notificar a la CNBV», plazo que no está en el art. 67 leído.
- Los términos no cubren claves ni el aviso a CONDUSEF.

Lo que sí está armado, también a propósito: el departamento de datos personales, el procedimiento KYC, la política de conflictos de interés, un inventario de activos con fecha de aprobación, el código de ética, el procedimiento SITI y la cita a la Circular 12/2018.

La retención de ISR/IVA de la LIF 2026 no se evalúa: Nube Pago se audita como IFPE, y esa regla es solo para IFC.
