---
title: BigQuery + IA: Bot de Text-to-SQL para marketing
description: Cómo conectar un modelo de lenguaje con Google BigQuery para crear un agente de Text-to-SQL seguro, de bajo costo y con respuestas exactas en segundos.
date: 2026-09-18
lang: es
tags: IA, BigQuery, Agentes, Python, SQL, Marketing
---

En cualquier equipo de marketing o analítica, la historia se repite cada semana: alguien de dirección o un cliente pregunta por Slack: **"¿Cuál fue el canal con mejor ROAS la semana pasada y cómo viene el CPA de Meta comparado con Google?"**.

El analista tiene que frenar lo que está haciendo, abrir la consola de **Google BigQuery**, buscar el dataset correcto, escribir una consulta de 30 líneas con agregaciones y filtros de fecha, esperar los resultados, copiarlos a una hoja de cálculo y redactar el mensaje. Quince minutos después, manda una respuesta que se lee en diez segundos.

Conectar un LLM para responder preguntas en lenguaje natural (Text-to-SQL) parece la solución inmediata. Pero si lo haces de forma ingenua —como en la mayoría de tutoriales de internet— tienes una bomba de tiempo: un bot sin guardrails genera consultas no optimizadas que hacen escaneos completos de 400 GB en BigQuery, disparan la factura de Google Cloud a cientos de dólares y pueden inventar tablas inexistentes.

> **Regla de ingeniería:**
> - **El error del Text-to-SQL ingenuo:** Conectar un bot directo a la base de datos sin capas intermedias. Alucina esquemas, no usa particiones y quema presupuesto de cómputo.
> - **La solución de producción:** Una **arquitectura desacoplada en 4 capas** con permisos estrictos de solo lectura (IAM Read-Only), un validador sintáctico en Python con *Dry Run* para auditar el costo antes de tocar los datos, y cálculo determinista en BigQuery.
> - **El resultado:** Cualquier miembro del equipo consulta millones de filas de pauta en Slack o WhatsApp sin tocar una sola línea de SQL y por menos de $0.003 USD por consulta.

Así está diseñada la arquitectura para que opere con seguridad y bajo costo en producción.

## Por qué los dashboards tradicionales se quedan cortos

Los tableros en **Looker Studio, Tableau o Power BI** son excelentes para el monitoreo habitual: revisar el ritmo de gasto mensual o verificar si el CTR general está dentro de lo esperado.

El problema aparece con las **preguntas ad-hoc**:
- *"¿Qué creativos de video tuvieron mayor retención en el último evento de descuentos?"*
- *"¿Cómo varió el costo por adquisición (CPA) en Colombia frente a México los días de quincena?"*
- *"¿Cuánto invertimos en campañas de tráfico frío frente a retargeting el último trimestre?"*

Construir una tarjeta o un filtro nuevo en un dashboard para cada duda puntual satura la vista y desgasta al equipo de BI. Aquí es donde un **Agente de Datos con IA** resuelve la fricción real.

## La arquitectura en 4 capas: de lenguaje natural a BigQuery

Para que un agente funcione en un entorno empresarial serio, no se le da acceso libre a la base de datos. Se implementa un **pipeline controlado en 4 fases**:

![Arquitectura de un Agente de IA para Marketing sobre BigQuery](../assets/img/bigquery-agent-architecture.webp)

### 1. Capa de Negocio (La Interfaz del Usuario)
El usuario (analista, director de medios o cliente) escribe su pregunta en el canal habitual: Slack, Microsoft Teams o un chat web interno. No necesita saber qué es un `JOIN`, ni cómo se estructuran las tablas en el data lakehouse.

### 2. Capa Semántica y Traducción (El LLM)
Un modelo con alta capacidad de razonamiento técnico (como Gemini o Claude) recibe la pregunta. El truco no es pasarle toda la base de datos, sino entregarle un **Diccionario de Esquema (Schema Context)** acotado:
- Nombres de las tablas principales (`campaigns_performance`, `conversions_attribution`).
- Reglas de negocio para métricas clave (por ejemplo: *"ROAS es revenue dividido entre spend, jamás el promedio de la columna de ratios"*).
- Particiones disponibles (generalmente por fecha de evento `event_date`).

Con este contexto, el modelo traduce la intención del usuario a una consulta SQL limpia en dialecto GoogleSQL.

### 3. Capa de Guardrails y Auditoría de Costos (Python)
Este es el paso crítico que casi todos los prototipos omiten:
- **Validación estricta de solo lectura:** Un parser AST en Python rechaza cualquier consulta que contenga comandos de modificación (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `GRANT`).
- **Auditoría de costo con Dry Run:** Antes de ejecutar la query en BigQuery, se evalúa con el parámetro `dry_run = True` del cliente oficial de Google Cloud. BigQuery responde en milisegundos indicando exactamente cuántos megabytes va a escanear **sin cobrar un solo centavo**. Si la consulta intenta procesar más de 500 MB (porque el usuario no acotó la fecha), el agente la frena y solicita especificar el rango temporal.

### 4. Capa de Ejecución Determinista y Síntesis
BigQuery procesa la query sobre millones de filas particionadas en milisegundos. Los datos tabulares resultantes vuelven al agente, quien redacta la síntesis ejecutiva con los hallazgos clave y, si corresponde, renderiza un gráfico interactivo.

## Cómo opera en la práctica

Así responde el agente cuando un Director de Medios interactúa con él:

![Demostración de chat de un Agente de Marketing conectado a BigQuery](../assets/img/bigquery-agent-chat-demo.webp)

El flujo es completamente transparente:
1. El usuario pregunta en lenguaje conversacional sobre el rendimiento de Cyberlunes.
2. El agente formula la consulta SQL respetando las particiones por fecha.
3. El motor de BigQuery escanea apenas **14.2 MB en 1.4 segundos**.
4. La respuesta final entrega los números consolidados exactos (Meta ROAS 4.32x vs Google ROAS 3.78x) y una conclusión estratégica inmediata.

## El Benchmark: Agente Ingenuo vs. Agente de Producción

La diferencia entre conectar un bot directamente a la base de datos y montar una arquitectura controlada con guardrails es radical:

![Benchmark: Agente de IA Ingenuo vs Agente de Producción en BigQuery](../assets/img/bigquery-guardrails-benchmark.webp)

| Factor de Evaluación | Agente Ingenuo (Text-to-SQL básico) | Agente de Producción (Arquitectura Controlada) |
| :--- | :--- | :--- |
| **Costo por consulta en GCP** | **$1.50 a $3.00 USD** (escaneos completos de 400+ GB) | **< $0.003 USD** (aprovecha particiones y clústeres) |
| **Tiempo de respuesta** | 10 a 20 segundos (riesgo de timeout en Slack) | **1 a 2 segundos** (respuesta casi instantánea) |
| **Seguridad de datos** | Vulnerable a alucinaciones o modificaciones | **100% blindado** (permisos IAM de lectura estricta) |
| **Consistencia matemática** | 70% (puede inventar fórmulas intermedias) | **100% exacto** (el cálculo lo ejecuta BigQuery) |

## Desafíos reales para implementarlo en tu equipo

Montar un sistema de este tipo entrega una ventaja competitiva gigante, pero exige resolver detalles de ingeniería que no vienen en ningún prompt:

1. **Taxonomía unificada de canales:** Si Meta llama al gasto `spend`, Google Ads lo llama `cost` y TikTok lo llama `stat_cost`, tu lakehouse en BigQuery debe exponer vistas normalizadas para que el modelo no se confunda de fuente.
2. **Estrategia de particionamiento:** Las tablas deben estar particionadas por día (`PARTITION BY DATE(date)`) y agrupadas en clústeres por canal y campaña para que las queries cuesten fracciones de centavo.
3. **Caché inteligente de consultas:** Si dos personas hacen preguntas similares durante la misma mañana, el sistema debe responder desde caché en memoria sin volver a consultar la base de datos.
4. **Mínimo privilegio en la nube:** La cuenta de servicio de Google Cloud (Service Account) debe contar exclusivamente con permisos de lectura sobre las tablas autorizadas (`roles/bigquery.dataViewer`).

La inteligencia artificial en datos de negocio no consiste en darle acceso total a un bot; consiste en construir la infraestructura y los guardrails para que el modelo trabaje con precisión, seguridad y costos bajo control.

---

## Preguntas frecuentes

### ¿Cómo evita el agente que se dispare la factura de BigQuery?
Utilizando el modo `dry_run = True` en la API de BigQuery. Esto permite calcular exactamente cuántos bytes escaneará la consulta antes de ejecutarla. Si el volumen supera el límite establecido (por ejemplo, 500 MB), la consulta se detiene automáticamente.

### ¿Puede el bot modificar o borrar datos accidentalmente?
No, por dos motivos: primero, un linter sintáctico en Python descarta cualquier instrucción que contenga comandos DDL o DML; segundo, la cuenta de servicio de Google Cloud solo tiene permisos de lectura estricta.

### ¿Qué tan rápido responde el agente en Slack o Teams?
Entre 1 y 3 segundos en promedio, siempre que las tablas de BigQuery estén correctamente particionadas por fecha y optimizadas con clústeres.
