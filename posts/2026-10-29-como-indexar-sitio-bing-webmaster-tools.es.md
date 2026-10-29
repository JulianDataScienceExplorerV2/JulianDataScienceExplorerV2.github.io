---
title: Cómo indexar tu sitio en Bing Webmaster Tools paso a paso
description: Guía práctica para verificar tu dominio, enviar el sitemap, corregir issues de SEO, configurar IndexNow y enviar URLs a Bing desde un script en Python.
date: 2026-10-29
lang: es
tags: SEO, Bing, IndexNow, GitHub Pages, Webmaster Tools, Python
---

Después de publicar un sitio en GitHub Pages, el paso siguiente es hacer que los buscadores lo encuentren. Bing suele ser más rápido que Google para indexar sitios nuevos, y su consola detecta problemas de SEO que muchas veces pasamos por alto.

En esta guía repaso exactamente lo que hice para indexar [mi portafolio](https://juliandatascienceexplorerv2.github.io/) en Bing Webmaster Tools: verificación de dominio, envío de sitemap, corrección de errores, configuración de IndexNow y un script para enviar URLs automáticamente.

## Paso 1: Verificar tu dominio en Bing Webmaster Tools

1. Entra a [Bing Webmaster Tools](https://www.bing.com/webmasters) e inicia sesión.
2. Haz clic en **Agregar un sitio**.
3. Ingresa tu dominio, por ejemplo `https://juliandatascienceexplorerv2.github.io/`.
4. Bing te dará varias opciones de verificación. La más sencilla para GitHub Pages es subir un archivo HTML o XML a la raíz del sitio.
5. Descarga el archivo de verificación (por ejemplo `BingSiteAuth.xml`) y colócalo en la raíz de tu repo.
6. Haz `git add`, `commit` y `push`.
7. Espera unos minutos y presiona **Verificar** en Bing.

Una vez verificado, Bing empieza a rastrear tu sitio automáticamente, aunque puedes acelerar el proceso con los siguientes pasos.

## Paso 2: Enviar tu sitemap

En el menú lateral de Bing Webmaster Tools ve a **Sitemaps**.

Ingresa la URL de tu sitemap:

```
https://juliandatascienceexplorerv2.github.io/sitemap.xml
```

Presiona **Enviar**. Bing procesará el archivo y te dirá si encontró errores. Si tu sitemap tiene URLs canónicas, `lastmod`, `changefreq` y `priority`, mucho mejor.

## Paso 3: Revisar y corregir los issues de SEO

Bing Webmaster Tools tiene una sección de **SEO Recommendations** o **Issues** donde detecta problemas comunes. En mi caso aparecieron dos:

### Títulos demasiado largos
Bing recomienda que los `<title>` no superen los 65 caracteres. Acorté títulos de posts y de la home para que encajen.

### Meta descriptions fuera de rango
Las descripciones deben tener entre 25 y 160 caracteres. Varias de mis páginas estaban por encima de 160, así que las recorté manteniendo el sentido.

Mi recomendación: revisa cada issue que te muestre Bing, corrige en el código fuente y regenera las páginas si usas un generador estático.

## Paso 4: Configurar IndexNow

IndexNow es un protocolo abierto que notifica a Bing (y otros buscadores) cuando publicas o actualizas URLs.

### Generar la API key

1. Genera un UUID de 8 a 128 caracteres. En macOS o Linux:

```bash
python3 -c "import uuid; print(uuid.uuid4())"
```

2. Crea un archivo de texto con el UUID como nombre y contenido. Si tu key es `abcd1234-...`, el archivo será:

```
abcd1234-....txt
```

3. Súbelo a la raíz de tu sitio. Debe ser accesible públicamente en:

```
https://juliandatascienceexplorerv2.github.io/abcd1234-....txt
```

> **Nota importante:** la key de IndexNow es pública por diseño. Sirve para verificar que controlas el dominio, no es un secret como una API key de OpenAI.

## Paso 5: Enviar URLs automáticamente con Python

Crea un script que lea tu `sitemap.xml` y envíe las URLs al endpoint de IndexNow. Yo uso este:

```python
#!/usr/bin/env python3
import os
import sys
import xml.etree.ElementTree as ET
import requests

INDEXNOW_ENDPOINT = "https://www.bing.com/indexnow"
SITEMAP_PATH = "sitemap.xml"
BATCH_SIZE = 100

def get_env(name):
    value = os.environ.get(name)
    if not value:
        print(f"Error: variable {name} no definida")
        sys.exit(1)
    return value

def load_urls(path):
    tree = ET.parse(path)
    root = tree.getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text.strip() for url in root.findall("sm:url", ns) for loc in [url.find("sm:loc", ns)] if loc is not None and loc.text]

def submit_batch(host, key, urls):
    payload = {
        "host": host,
        "key": key,
        "keyLocation": f"https://{host}/{key}.txt",
        "urlList": urls,
    }
    return requests.post(INDEXNOW_ENDPOINT, json=payload, timeout=30)

def main():
    key = get_env("INDEXNOW_KEY")
    host = get_env("SITE_HOST")
    urls = load_urls(SITEMAP_PATH)
    print(f"URLs encontradas: {len(urls)}")

    for i in range(0, len(urls), BATCH_SIZE):
        batch = urls[i:i+BATCH_SIZE]
        resp = submit_batch(host, key, batch)
        print(f"Lote {i//BATCH_SIZE + 1}: HTTP {resp.status_code}")
        if resp.status_code not in (200, 202):
            print(resp.text)
            sys.exit(1)

if __name__ == "__main__":
    main()
```

Ejecútalo así:

```bash
export INDEXNOW_KEY="tu-key-aqui"
export SITE_HOST="juliandatascienceexplorerv2.github.io"
python3 scripts/submit_indexnow.py
```

Si todo va bien verás:

```
Found 17 URLs in sitemap.xml
Sending batch 1/1 (17 URLs)...
HTTP 200
OK - URLs accepted for processing
```

## Paso 6: Verificar que Bing recibió las URLs

IndexNow responde de inmediato, pero la consola de Bing puede tardar horas o días en reflejarlo. Para confirmar:

1. Revisa que tu key sea pública:
   ```
   https://juliandatascienceexplorerv2.github.io/tu-key.txt
   ```

2. Dentro de unos días busca en Bing:
   ```
   site:juliandatascienceexplorerv2.github.io
   ```

Eso te mostrará cuántas páginas de tu sitio están indexadas.

## Conclusión

Bing Webmaster Tools es una herramienta poderosa y subestimada. No solo indexa más rápido que Google en muchos casos, sino que también te dice exactamente qué arreglar en tu HTML antes de que Google lo note.

Si sigues estos pasos, tu sitio en GitHub Pages estará verificado, indexado y notificado automáticamente cada vez que publiques contenido nuevo.
