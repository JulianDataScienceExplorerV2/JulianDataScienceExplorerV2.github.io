---
title: Como indexar seu site no Bing Webmaster Tools passo a passo
description: Guia prático para verificar seu domínio, enviar o sitemap, corrigir issues de SEO, configurar o IndexNow e enviar URLs para o Bing usando um script Python.
date: 2026-10-29
lang: pt
tags: SEO, Bing, IndexNow, GitHub Pages, Webmaster Tools, Python
---

Depois de publicar um site no GitHub Pages, o próximo passo é fazer com que os mecanismos de busca o encontrem. O Bing costuma ser mais rápido que o Google para indexar sites novos, e sua console detecta problemas de SEO que muitas vezes passam despercebidos.

Neste guia vou contar exatamente o que fiz para indexar [meu portfólio](https://juliandatascienceexplorerv2.github.io/) no Bing Webmaster Tools: verificação de domínio, envio de sitemap, correção de erros, configuração do IndexNow e um script para enviar URLs automaticamente.

## Passo 1: Verificar seu domínio no Bing Webmaster Tools

1. Acesse o [Bing Webmaster Tools](https://www.bing.com/webmasters) e faça login.
2. Clique em **Adicionar um site**.
3. Insira seu domínio, por exemplo `https://juliandatascienceexplorerv2.github.io/`.
4. O Bing oferece várias opções de verificação. A mais simples para GitHub Pages é fazer upload de um arquivo HTML ou XML na raiz do site.
5. Baixe o arquivo de verificação (por exemplo `BingSiteAuth.xml`) e coloque-o na raiz do seu repositório.
6. Execute `git add`, `commit` e `push`.
7. Aguarde alguns minutos e pressione **Verificar** no Bing.

Uma vez verificado, o Bing começa a rastrear seu site automaticamente, embora você possa acelerar o processo com os passos a seguir.

## Passo 2: Enviar seu sitemap

No menu lateral do Bing Webmaster Tools, vá em **Sitemaps**.

Insira a URL do seu sitemap:

```
https://juliandatascienceexplorerv2.github.io/sitemap.xml
```

Pressione **Enviar**. O Bing processará o arquivo e informará se encontrou erros. Um sitemap com URLs canônicas, `lastmod`, `changefreq` e `priority` funciona melhor.

## Passo 3: Revisar e corrigir issues de SEO

O Bing Webmaster Tools tem uma seção de **Recomendações de SEO** ou **Issues** onde detecta problemas comuns. No meu caso apareceram dois:

### Títulos muito longos
O Bing recomenda que as tags `<title>` não ultrapassem 65 caracteres. Eu encurtei títulos dos posts e da home para que ficassem dentro do limite.

### Meta descriptions fora do intervalo
As descrições devem ter entre 25 e 160 caracteres. Várias das minhas páginas estavam acima de 160, então eu as reduzi mantendo o sentido.

Minha recomendação: revise cada issue que o Bing mostrar, corrija no código-fonte e regenera as páginas se usar um gerador estático.

## Passo 4: Configurar o IndexNow

O IndexNow é um protocolo aberto que notifica o Bing (e outros buscadores) quando você publica ou atualiza URLs.

### Gerar a API key

1. Gere um UUID entre 8 e 128 caracteres. No macOS ou Linux:

```bash
python3 -c "import uuid; print(uuid.uuid4())"
```

2. Crie um arquivo de texto com o UUID como nome e conteúdo. Se sua key for `abcd1234-...`, o arquivo será:

```
abcd1234-....txt
```

3. Faça upload na raiz do seu site. Ele deve estar acessível publicamente em:

```
https://juliandatascienceexplorerv2.github.io/abcd1234-....txt
```

> **Nota importante:** a key do IndexNow é pública por design. Serve para verificar que você controla o domínio, não é um secret como uma API key da OpenAI.

## Passo 5: Enviar URLs automaticamente com Python

Crie um script que leia seu `sitemap.xml` e envie as URLs para o endpoint do IndexNow. Eu uso este:

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
        print(f"Erro: variável de ambiente {name} não definida")
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

Execute assim:

```bash
export INDEXNOW_KEY="sua-key-aqui"
export SITE_HOST="juliandatascienceexplorerv2.github.io"
python3 scripts/submit_indexnow.py
```

Se tudo der certo, você verá:

```
Found 17 URLs in sitemap.xml
Sending batch 1/1 (17 URLs)...
HTTP 200
OK - URLs accepted for processing
```

## Passo 6: Verificar se o Bing recebeu as URLs

O IndexNow responde imediatamente, mas a console do Bing pode levar horas ou dias para refletir. Para confirmar:

1. Verifique se sua key está pública:
   ```
   https://juliandatascienceexplorerv2.github.io/sua-key.txt
   ```

2. Depois de alguns dias, busque no Bing:
   ```
   site:juliandatascienceexplorerv2.github.io
   ```

Isso mostrará quantas páginas do seu site estão indexadas.

## Conclusão

O Bing Webmaster Tools é uma ferramenta poderosa e subestimada. Além de indexar mais rápido que o Google em muitos casos, ele também diz exatamente o que corrigir no seu HTML antes que o Google note.

Se você seguir estes passos, seu site no GitHub Pages estará verificado, indexado e notificado automaticamente sempre que publicar conteúdo novo.
