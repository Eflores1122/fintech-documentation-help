# Catálogo de reglas

Cada año regulatorio vive en su carpeta (`rules/2025`, `rules/2026`). Dentro, una carpeta por área (`legal`, `regulatorio`, `financiero`, `fiscal`, `pld`, `ciberseguridad`, `privacidad`, `condusef`, `riesgos`, `operacion`, `laboral`, `metodologia`, `meta`). El año de la carpeta tiene que coincidir con `catalog_year`. Los YAML sueltos en la raíz del año siguen siendo válidos.

Campos que no pueden faltar: `id`, `source_url` (https, fuente oficial), `source_name`, `effective_date`, `last_verified`, `severity`, `fix_suggestion` y `matcher`.

`unverified: true` (equivalente a `verified: false`) significa que el detalle fino (número de regla de la RMF, encuadre exacto, plazo) no se leyó completo en el instrumento. Esa bandera se imprime en `fdh rules validate`, en `fdh rules list` y en el reporte. No la quite para “limpiar” la salida.

`applies_if` solo puede ser una bandera del perfil: `operates_virtual_assets`, `has_partial_or_deferred_payments`, `transports_goods`, `is_technological_platform_tax_regime`, `provides_digital_services_liva`, `processes_cards`, `participates_spei`, `uses_specialized_services`, `offers_credit`, `offers_yield`, `has_related_parties_abroad`. Si el usuario no la activa, la regla sale como no aplicable.

`min_strictness: max` reserva la regla para el modo estricto, que es el default. `binding: false` marca referencia internacional o criterio de auditoría, no ley mexicana.

El esquema de referencia está en `schemas/rule.schema.json`. Quien valida en ejecución es Pydantic (`fdh rules validate`).

Estas reglas no son asesoría legal ni fiscal.
