# Catálogo de reglas

Cada año regulatorio vive en su carpeta (`rules/2025`, `rules/2026`). Los archivos YAML se parten por dominio. El año de la carpeta tiene que coincidir con `catalog_year`.

Campos que no pueden faltar: `id`, `source_url` (https, fuente oficial), `source_name`, `effective_date`, `last_verified`, `severity`, `fix_suggestion` y `matcher`.

`unverified: true` significa que el detalle fino (número de regla de la RMF, encuadre exacto, plazo) no se leyó completo en el instrumento. Esa bandera se imprime en `fdh rules validate`, en `fdh rules list` y en el reporte. No la quite para “limpiar” la salida.

`applies_if` solo puede ser una de las banderas del perfil (`operates_virtual_assets`, `has_partial_or_deferred_payments`, `transports_goods`, `is_technological_platform_tax_regime`, `provides_digital_services_liva`). Si el usuario no la activa, la regla sale como no aplicable.

El esquema de referencia está en `schemas/rule.schema.json`. Quien valida en ejecución es Pydantic (`fdh rules validate`).

Estas reglas no son asesoría legal ni fiscal.
