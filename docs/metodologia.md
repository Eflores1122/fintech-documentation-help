# Metodología de auditoría

Esta herramienta no es asesoría legal ni fiscal, ni un dictamen de auditor externo. Es un examen documental: compara expedientes sintéticos o los que usted cargue contra un catálogo de reglas con cita y fecha de verificación.

## Estrictez

El default es `--strictness max`, el auditor más exigente.

| Nivel | Qué corre |
|---|---|
| `standard` | Reglas del catálogo del año y de la figura. |
| `high` | Lo mismo. Reservado para reglas que se marquen `min_strictness: high`. |
| `max` | Además penaliza, como criterio de auditoría y no como artículo de la CNBV, la falta de fecha de aprobación, los placeholders («por definir», «borrador», «TBD»), las versiones de trabajo y el texto que admite no tener evidencia. |

Un hallazgo de estas reglas de metodología lleva `binding: false`. No se presenta como norma mexicana.

## Fases

1. **Planeación.** Tipo de entidad y perfil (activos virtuales, SPEI, tarjetas, crédito, rendimiento, REPSE, partes relacionadas en el extranjero).
2. **Inventario.** Tipos de documento que las reglas esperan frente a los que se clasificaron.
3. **Revisión documental.** Chequeos determinísticos. Son la base.
4. **Pruebas de controles.** Un JSON `rule_id → presente|ausente|parcial`. «Presente» no borra un fallo del texto. «Ausente» puede abrir un fallo que el texto había dejado en cumple.
5. **Hallazgos.** Cada incumplimiento trae condición, criterio, causa, efecto, recomendación, evidencia requerida, responsable sugerido y plazo sugerido, más la fuente.
6. **Remediación.** Plan con estado `abierto`.
7. **Seguimiento.** `fdh audit ... --compare informe-anterior.json`.
8. **Dictamen.** Calificación por área y global. Si hay un crítico, el dictamen documental es adverso. No es una opinión de estados financieros.

## Qué hace la IA y qué no

Sin modelo, todo lo anterior corre. Si enciende un modelo local (Ollama, llama.cpp, LM Studio, vLLM u otro endpoint compatible), el modelo solo puede citar un `rule_id` del catálogo y un fragmento literal del archivo. Los hallazgos que toca quedan con `source: mixed` y una confianza. No baja la severidad. El modo `--adversarial` pide más fallas, no menos.

Los documentos no salen de la máquina salvo `FDH_LLM_ALLOW_REMOTE=1`.

## Áreas

Cada área tiene procedimiento en `fdh.areas.AREA_PROCEDURES` y reglas en `rules/<año>/<área>/`. Las áreas son: legal, regulatorio, financiero, fiscal, PLD/FT, ciberseguridad, privacidad, CONDUSEF, riesgos, operación y laboral. Metodología y meta no son obligaciones de la entidad.

## Calificación

Peso: crítico 5, alto 3, medio 2, bajo 1, info 0. Cumplir vale el peso, no concluyente la mitad, fallar cero. «No aplica» sale del denominador. Info no mueve el número, pero se ve.

Los marcos ISO 27001:2022, NIST CSF 2.0, PCI DSS 4.0, SOC 2, COSO y las 40 recomendaciones del GAFI están como referencia. El informe dice que no son obligatorios en México. PCI solo entra si el perfil declara que procesa tarjetas.
