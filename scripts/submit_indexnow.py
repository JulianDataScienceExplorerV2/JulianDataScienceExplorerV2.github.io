#!/usr/bin/env python3
"""
Submit URLs from sitemap.xml to IndexNow (Bing, Yandex, Naver, etc.).

Usage:
    export INDEXNOW_KEY="tu-key-aqui"
    export SITE_HOST="juliandatascienceexplorerv2.github.io"
    python3 scripts/submit_indexnow.py

The API key must be available as a plain-text file at:
    https://{SITE_HOST}/{INDEXNOW_KEY}.txt

Never commit the key file or .env to Git.
"""
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
        print(f"Error: environment variable {name} is not set.")
        sys.exit(1)
    return value


def load_urls_from_sitemap(path):
    tree = ET.parse(path)
    root = tree.getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = []
    for url in root.findall("sm:url", ns):
        loc = url.find("sm:loc", ns)
        if loc is not None and loc.text:
            urls.append(loc.text.strip())
    return urls


def submit_batch(host, key, urls):
    payload = {
        "host": host,
        "key": key,
        "keyLocation": f"https://{host}/{key}.txt",
        "urlList": urls,
    }
    resp = requests.post(INDEXNOW_ENDPOINT, json=payload, timeout=30)
    return resp


def main():
    key = get_env("INDEXNOW_KEY")
    host = get_env("SITE_HOST")

    if not os.path.exists(SITEMAP_PATH):
        print(f"Error: {SITEMAP_PATH} not found.")
        sys.exit(1)

    urls = load_urls_from_sitemap(SITEMAP_PATH)
    print(f"Found {len(urls)} URLs in {SITEMAP_PATH}")

    total_batches = (len(urls) + BATCH_SIZE - 1) // BATCH_SIZE
    for i in range(0, len(urls), BATCH_SIZE):
        batch = urls[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"\nSending batch {batch_num}/{total_batches} ({len(batch)} URLs)...")
        resp = submit_batch(host, key, batch)
        print(f"HTTP {resp.status_code}")
        if resp.status_code in (200, 202):
            print("OK - URLs accepted for processing")
        else:
            print(f"Error: {resp.text}")
            sys.exit(1)

    print("\nAll batches submitted successfully.")


if __name__ == "__main__":
    main()
