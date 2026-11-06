# Seguridad

## Documentos confidenciales y modelos de lenguaje

La auditoría determinística corre en local. No necesita clave ni red.

El revisor opcional (`fdh audit --llm` o la casilla de la interfaz) **envía el texto de los documentos** al endpoint compatible con OpenAI configurado en `FDH_LLM_BASE_URL` (por omisión `https://api.openai.com/v1`), usando `FDH_LLM_API_KEY`.

No active esa opción con avisos de privacidad reales, contratos, expedientes KYC, listados de clientes, manuales internos ni ningún otro documento confidencial. Esos archivos no deben salir hacia un proveedor externo. Sin la clave, o sin la bandera `--llm`, ningún texto se envía.

La interfaz web (`fdh serve`) escucha en `127.0.0.1` por omisión y deja la casilla del modelo apagada. Sigue siendo un proceso local: no lo exponga a internet con documentos de clientes.

## Qué hace el revisor si se enciende

Solo se conservan hallazgos cuyo `rule_id` existe en el catálogo del año elegido y cuya cita es un fragmento literal del archivo ingerido. Una obligación que el modelo redacte y que no esté en el catálogo se descarta y se lista como hallazgo rechazado. Eso limita invención regulatoria; no convierte al proveedor en un lugar seguro para datos personales o secretos de negocio.

## Reportes

Los reportes son un checklist. No son asesoría legal ni fiscal. Las reglas `UNVERIFIED` siguen a la vista hasta que alguien lea el instrumento oficial completo.

## Dependencias

Las vulnerabilidades de las librerías se atienden por los canales habituales del repositorio. No hay un programa de recompensas.
