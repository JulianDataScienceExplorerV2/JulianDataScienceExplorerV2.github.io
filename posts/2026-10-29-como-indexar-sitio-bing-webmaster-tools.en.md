---
title: How to Index Your Site in Bing Webmaster Tools Step by Step
description: Practical guide to verify your domain, submit a sitemap, fix SEO issues, set up IndexNow, and submit URLs to Bing using a Python script.
date: 2026-10-29
lang: en
tags: SEO, Bing, IndexNow, GitHub Pages, Webmaster Tools, Python
---

After publishing a site on GitHub Pages, the next step is making sure search engines can find it. Bing is often faster than Google at indexing new sites, and its console catches SEO issues that are easy to overlook.

In this guide I walk through exactly what I did to index [my portfolio](https://juliandatascienceexplorerv2.github.io/) in Bing Webmaster Tools: domain verification, sitemap submission, fixing SEO issues, configuring IndexNow, and automating URL submissions with a script.

## Step 1: Verify your domain in Bing Webmaster Tools

1. Go to [Bing Webmaster Tools](https://www.bing.com/webmasters) and sign in.
2. Click **Add a site**.
3. Enter your domain, for example `https://juliandatascienceexplorerv2.github.io/`.
4. Bing gives you several verification options. The easiest for GitHub Pages is uploading an HTML or XML file to the site root.
5. Download the verification file (for example `BingSiteAuth.xml`) and place it in your repo root.
6. Run `git add`, `commit`, and `push`.
7. Wait a few minutes, then click **Verify** in Bing.

Once verified, Bing starts crawling your site automatically, though you can speed things up with the steps below.

## Step 2: Submit your sitemap

In the Bing Webmaster Tools sidebar, go to **Sitemaps**.

Enter your sitemap URL:

```
https://juliandatascienceexplorerv2.github.io/sitemap.xml
```

Click **Submit**. Bing will process the file and tell you if it found errors. A sitemap with canonical URLs, `lastmod`, `changefreq`, and `priority` works best.

## Step 3: Review and fix SEO issues

Bing Webmaster Tools has an **SEO Recommendations** or **Issues** section that detects common problems. In my case it flagged two:

### Titles too long
Bing recommends keeping `<title>` tags under about 65 characters. I shortened post titles and the home page title to fit.

### Meta descriptions out of range
Descriptions should be between 25 and 160 characters. Several of my pages were over 160, so I trimmed them while keeping the meaning.

My recommendation: review every issue Bing shows, fix it in your source code, and regenerate the pages if you use a static site generator.

## Step 4: Set up IndexNow

IndexNow is an open protocol that notifies Bing (and other search engines) when you publish or update URLs.

### Generate an API key

1. Generate a UUID between 8 and 128 characters. On macOS or Linux:

```bash
python3 -c "import uuid; print(uuid.uuid4())"
```

2. Create a text file named after the UUID with the same content. If your key is `abcd1234-...`, the file is:

```
abcd1234-....txt
```

3. Upload it to your site root. It must be publicly accessible at:

```
https://juliandatascienceexplorerv2.github.io/abcd1234-....txt
```

> **Important note:** the IndexNow key is public by design. It is used to verify domain ownership, not as a secret like an OpenAI API key.

## Step 5: Submit URLs automatically with Python

Create a script that reads your `sitemap.xml` and sends URLs to the IndexNow endpoint. Here is the one I use:

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
        print(f"Error: environment variable {name} not set")
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
    print(f"Found {len(urls)} URLs")

    for i in range(0, len(urls), BATCH_SIZE):
        batch = urls[i:i+BATCH_SIZE]
        resp = submit_batch(host, key, batch)
        print(f"Batch {i//BATCH_SIZE + 1}: HTTP {resp.status_code}")
        if resp.status_code not in (200, 202):
            print(resp.text)
            sys.exit(1)

if __name__ == "__main__":
    main()
```

Run it like this:

```bash
export INDEXNOW_KEY="your-key-here"
export SITE_HOST="juliandatascienceexplorerv2.github.io"
python3 scripts/submit_indexnow.py
```

If everything works you will see:

```
Found 17 URLs in sitemap.xml
Sending batch 1/1 (17 URLs)...
HTTP 200
OK - URLs accepted for processing
```

## Step 6: Verify that Bing received the URLs

IndexNow responds immediately, but the Bing console can take hours or days to reflect the submission. To confirm:

1. Make sure your key is public:
   ```
   https://juliandatascienceexplorerv2.github.io/your-key.txt
   ```

2. After a few days, search on Bing:
   ```
   site:juliandatascienceexplorerv2.github.io
   ```

This will show you how many pages of your site are indexed.

## Conclusion

Bing Webmaster Tools is a powerful and underrated tool. It often indexes faster than Google and tells you exactly what to fix in your HTML before Google even notices.

If you follow these steps, your GitHub Pages site will be verified, indexed, and automatically notified every time you publish new content.
