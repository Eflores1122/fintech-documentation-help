## Qué cambia

<!-- Catálogo, motor, muestras o documentación. -->

## Reglas nuevas o modificadas

- [ ] Cada regla nueva o editada trae `source_url` **https** a una fuente oficial (DOF, Cámara de Diputados, SAT, CNBV, Banxico, CONDUSEF o UIF).
- [ ] `effective_date` y `last_verified` están en formato `YYYY-MM-DD`.
- [ ] Si el PDF o la disposición no se leyó completa, la regla lleva `unverified: true` y `unverified_detail` que dice qué falta por leer. La bandera no se esconde.
- [ ] Hay `fix_suggestion` concreta y, si el cambio es anual, `diff_note`.
- [ ] Si la regla reemplaza a otra, `supersedes` apunta a un id que existe en algún año del catálogo.
- [ ] No se inventaron números de artículo, tasas ni plazos que no estén en la fuente.

### URL oficial

<!-- Pegue la URL. Si son varias, una por línea. -->

### Diff

<!-- Salida relevante de `fdh rules diff AÑO_ANTERIOR AÑO_NUEVO`. -->

## Verificación

- [ ] `fdh rules validate`
- [ ] `fdh rules citations` (si aparece una regla en MISSING SOURCE, no se inventa la URL)
- [ ] `pytest`

## Aviso

Este cambio no es asesoría legal ni fiscal.
