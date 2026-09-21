---
title: Cómo generé un dashboard de marketing con IA en 2 minutos
description: Construí una herramienta que convierte un CSV de campañas en un dashboard listo para el cliente, con análisis escrito por IA. Así funciona y así lo replicas.
date: 2026-09-17
tags: IA, Marketing, Automatización, Python
---

En agencia, el reporte mensual es siempre el mismo ritual: abres el export de Meta, el de Google, pegas todo en Excel, armas las tablas dinámicas, revisas que los números cuadren, haces los gráficos y escribes el análisis. Tres horas después tienes algo que el cliente mira cinco minutos.

Construí una herramienta para eliminar ese ritual: **mktdash**. Subes el archivo de campañas y en segundos tienes KPIs, gráficos y un resumen ejecutivo escrito por IA, todo exportable en un solo HTML con la marca de tu agencia.

## El problema real no es hacer gráficos

Hacer un gráfico es fácil. El problema es todo lo que pasa **antes**: cada plataforma exporta columnas con nombres distintos, en español o en inglés, y cada cliente pide métricas diferentes. La parte cara del reporte es la traducción: entender qué columna es qué, calcular los KPIs correctos y contar la historia con esos números.

Ahí la IA es perfecta para una mitad del trabajo y peligrosa para la otra.

## La arquitectura: IA para entender, código para calcular

El error común es pedirle a un modelo que "genere el dashboard". Los modelos de lenguaje escriben texto convincente, pero no son confiables para calcular. Un ROAS mal calculado en un reporte de cliente es un problema serio.

Por eso separé responsabilidades:

- **Gemini hace lo que se le da bien**: lee los nombres de tus columnas más cinco filas de muestra y deduce el mapeo (por ejemplo, que "Inversión" es el gasto y "Campaña" es la dimensión). Después lee la tabla de KPIs ya calculados y escribe el resumen ejecutivo.
- **Python calcula todo**: el motor en pandas computa inversión, ingresos, ROAS, conversiones, CPA, CTR, CPC, CPM, CVR. Los gráficos salen con Plotly. Cero números inventados.

La regla es simple: **la IA interpreta y narra; el código calcula**. Si el modelo falla o no hay API key, el sistema sigue funcionando con detección de columnas por nombre y sin resumen.

## Qué genera

Con un CSV de 90 días de Meta, Google y TikTok, la herramienta produce:

- Once KPIs con formato listo para presentar.
- Inversión vs ingresos en el tiempo, evolución de eficiencia, comparativo por canal, top campañas y funnel de conversión.
- Un resumen ejecutivo de cinco bullets con hallazgos y acciones.
- Un reporte HTML autocontenido que puedes enviar por correo o imprimir como PDF.

El motor es determinista: el mismo archivo produce siempre los mismos números. Eso es lo que te permite defenderlo frente a un cliente.

## Lo que aprendí construyéndolo

1. **Los nombres de columnas son un caos.** El mismo dato se llama `spend`, `Cost`, `Inversión` o `importe_gastado`. Un buen mapeo resuelve el 80% de la fricción de adopción.
2. **La gente no confía en lo que no puede editar.** Mostrar qué columna se mapeó a qué campo (y permitir corregirlo) vale más que cualquier promesa de precisión.
3. **Los datos vienen sucios.** Monedas con símbolos, comas como decimales, fechas en formatos distintos. La validación es la mitad del trabajo.
4. **El resumen ejecutivo es lo que se vende.** Los gráficos ya existían en la plataforma de anuncios; la traducción a decisiones es lo que ahorra tiempo.

## Cómo lo replicas

El stack es corto: Python, pandas, Plotly y la API de Gemini. La versión que corre localmente son unas 400 líneas más el motor de métricas; la versión web agrega FastAPI y Next.js.

Si quieres montar algo así en tu agencia o tu equipo, necesitas tres cosas: un export limpio de campañas, una API key de Gemini y decidir qué KPIs le importan a tu cliente. El resto es plomería.

Si te sirve este tipo de contenido, estoy publicando acá las decisiones técnicas y de negocio detrás de lo que construyo. Y si quieres que lo lleve a tu equipo, escríbeme.
