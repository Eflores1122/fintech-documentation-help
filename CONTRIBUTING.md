# Cómo contribuir

Este repositorio no da asesoría legal ni fiscal. Las reglas son un checklist con cita a fuentes públicas. Quien fusione un cambio de fondo regulatorio confirma la URL, no “completa” el derecho con memoria del modelo.

## Entorno

Python 3.12.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
ruff check src tests scripts
ruff format --check src tests scripts
pytest
```

## Actualización anual (diciembre–enero) y reformas

La Resolución Miscelánea Fiscal y la Ley de Ingresos se renuevan por ejercicio. Otras piezas (LFPDPPP, LFPIORPI, disposiciones de CNBV, Banxico o CONDUSEF) entran cuando se publican. El catálogo sigue ese calendario: una carpeta por año, no un archivo que se reescribe y pierde la historia.

1. Copie `rules/<año anterior>/` a `rules/<año nuevo>/`.
2. En cada YAML, ponga `catalog_year` igual al nombre de la carpeta.
3. Para cada obligación que cambió:
   - actualice `requirement`, `source_url`, `source_name`, `effective_date` y `last_verified`;
   - escriba `diff_note` en español, diciendo qué cambió y por qué importa;
   - si la regla nueva reemplaza a otra, use un id nuevo y `supersedes` con el id anterior; deje la regla vieja solo en el año en que estuvo vigente;
   - si el PDF, el anexo o la regla numerada no se leyeron completos, deje `unverified: true` y explique en `unverified_detail` qué falta. No borre la bandera para que el reporte se vea más limpio.
4. No agregue números de artículo, tasas, plazos ni nombres de regla que no estén en la fuente que acaba de abrir. Si la semilla de investigación marcó un punto como no verificado, se queda así hasta que alguien lea el instrumento.
5. La `source_url` tiene que ser `https://` y de un sitio oficial: Diario Oficial de la Federación, Cámara de Diputados, SAT, CNBV, Banxico, CONDUSEF o UIF. Un resumen de despacho no sustituye esa URL.
6. Corra:

```bash
fdh rules validate
fdh rules diff <año anterior> <año nuevo>
```

7. Pegue en el pull request el diff y la URL. La plantilla de PR (`.github/PULL_REQUEST_TEMPLATE.md`) no se puede dar por llenada sin la URL oficial.
8. Si hace falta un documento sintético nuevo, use una entidad ficticia. No copie políticas, contratos ni datos de una empresa real.

Cadencia práctica:

- **Anual (diciembre–enero):** RMF, anexos y LIF del ejercicio.
- **Cuando salga una resolución de modificaciones:** ajuste la regla afectada o marque el seguimiento en el calendario fiscal; no hace falta un año de catálogo distinto si la obligación sigue siendo la del mismo ejercicio.
- **Cuando el DOF publique una reforma de ley o disposición:** regla nueva o `diff_note`, con vigencia del propio decreto.

## Motor y muestras

Los chequeos determinísticos viven en `matcher` dentro del YAML. El revisor de modelo de lenguaje, si alguien lo enciende, solo puede citar un `id` de ese catálogo y un fragmento que esté en el documento. No añada lógica que acepte una obligación inventada por el modelo.

`samples/nube_pago/` es ficticia. Si cambia un matcher, regenere el reporte dorado y revise el diff del ejemplo:

```bash
fdh audit samples/nube_pago/docs --year 2026 --entity IFPE --out /tmp/fdh-report
```

Los tests comparan estatus, severidad y URL de cada hallazgo contra `examples/nube_pago/report.json`.
