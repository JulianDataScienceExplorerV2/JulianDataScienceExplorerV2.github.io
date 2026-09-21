#!/usr/bin/env python3
import html
import os
import re
from datetime import datetime, timezone
from email.utils import format_datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, "posts")
BLOG_DIR = os.path.join(ROOT, "blog")
SITE = "https://juliandatascienceexplorerv2.github.io"
AUTHOR = "Julian David Urrego Lancheros"

POST_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title} — Julian David Urrego Lancheros</title>
<meta name="description" content="{description}" />
<meta name="theme-color" content="#07070a" />
<link rel="canonical" href="{url}" />
<meta property="og:type" content="article" />
<meta property="og:url" content="{url}" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{description}" />
<meta property="og:image" content="{site}/og-image.png" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{title}" />
<meta name="twitter:description" content="{description}" />
<meta name="twitter:image" content="{site}/og-image.png" />
<link rel="icon" type="image/png" href="{base}favicon.png" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="{base}assets/style.css" />
<script type="application/ld+json">
{jsonld}
</script>
</head>
<body>
<nav>
  <a class="nav-logo" href="{base}" style="text-decoration:none">&gt;<span class="d"> julian</span>.dev</a>
  <ul class="nav-links">
    <li><a href="{base}">{home}</a></li>
    <li><a href="{base}blog/">{blog}</a></li>
  </ul>
</nav>

<div class="section" style="padding-top:7rem">
  <div class="wrap" style="max-width:760px">
    <p class="kicker"><a href="{base}blog/" style="color:inherit;text-decoration:none">&larr; Volver al blog</a></p>
    <h1 class="sec-h" style="font-size:2rem;line-height:1.2">{title}</h1>
    <p class="sec-s" style="margin-bottom:2rem">{date_label} · {reading} min · {tags}</p>
    <article class="post">
{content}
    </article>
    <div class="dl" style="margin-top:3rem">
      <p style="font-size:14px;color:var(--text-2);line-height:1.7">
        {cta_text}
      </p>
      <div style="display:flex;gap:.75rem;flex-wrap:wrap">
        <a class="cta1" href="{base}#contact">{cta_label}</a>
        <a class="cta2" href="{base}">{portfolio_label}</a>
      </div>
    </div>
  </div>
</div>

<footer>Julian David Urrego Lancheros &mdash; <span class="hi">juliandatascienceexplorerv2.github.io</span></footer>
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Blog — Julian David Urrego Lancheros</title>
<meta name="description" content="IA aplicada, marketing science y datos para negocios en LATAM. Guías prácticas con ejemplos y código." />
<meta name="theme-color" content="#07070a" />
<link rel="canonical" href="{site}/blog/" />
<meta property="og:type" content="website" />
<meta property="og:url" content="{site}/blog/" />
<meta property="og:title" content="Blog — Julian David Urrego Lancheros" />
<meta property="og:description" content="IA aplicada, marketing science y datos para negocios en LATAM." />
<meta property="og:image" content="{site}/og-image.png" />
<link rel="alternate" type="application/rss+xml" title="Blog de Julian Urrego" href="{site}/blog/feed.xml" />
<link rel="icon" type="image/png" href="../favicon.png" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
<link rel="stylesheet" href="../assets/style.css" />
</head>
<body>
<nav>
  <a class="nav-logo" href="../" style="text-decoration:none">&gt;<span class="d"> julian</span>.dev</a>
  <ul class="nav-links">
    <li><a href="../">Portafolio</a></li>
    <li><a href="./">Blog</a></li>
  </ul>
</nav>

<div class="section" style="padding-top:7rem">
  <div class="wrap">
    <p class="kicker">Blog</p>
    <h1 class="sec-h">IA aplicada y datos para negocios</h1>
    <p class="sec-s">Guías prácticas, experimentos y aprendizajes sobre IA, automatización y analítica en LATAM. Con ejemplos reales, no teoría.</p>
    <div class="post-list">
{cards}
    </div>
  </div>
</div>

<footer>Julian David Urrego Lancheros &mdash; <span class="hi">juliandatascienceexplorerv2.github.io</span></footer>
</body>
</html>
"""

POST_CARD = """      <a class="proj-card" href="{url}">
        <div class="ctop">
          <div class="cicon"><svg viewBox="0 0 24 24"><path d="M4 4h16v2H4zM4 9h10v2H4zM4 14h16v2H4zM4 19h10v2H4z"/></svg></div>
          <span class="ctime">{date_label}</span>
        </div>
        <p class="cname">{title}</p>
        <p class="cdesc">{description}</p>
        <div class="cfoot"><div class="tags">{tags_html}</div><span class="ctime">{reading} min</span></div>
      </a>
"""

BLOCK_JSONLD = """{{"@context":"https://schema.org","@type":"BlogPosting","headline":"{title}","description":"{description}","datePublished":"{date}","dateModified":"{date}","inLanguage":"{lang}","author":{{"@type":"Person","name":"{author}","url":"{site}"}},"publisher":{{"@type":"Person","name":"{author}"}},"mainEntityOfPage":"{url}","image":"{site}/og-image.png"}}"""

MONTHS = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def parse_front_matter(text):
    meta = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    key, _, value = line.partition(":")
                    meta[key.strip()] = value.strip()
            body = parts[2].strip()
    return meta, body


def esc(text):
    return html.escape(text, quote=False)


def inline(text):
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)
    return text


def md_to_html(raw):
    text = esc(raw)
    lines = text.split("\n")
    out = []
    paragraph = []
    list_open = None
    i = 0

    def flush_paragraph():
        if paragraph:
            out.append("<p>" + inline(" ".join(paragraph)) + "</p>")
            paragraph.clear()

    def close_list():
        nonlocal list_open
        if list_open:
            out.append(f"</{list_open}>")
            list_open = None

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            flush_paragraph()
            close_list()
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            out.append("<pre><code>" + "\n".join(code) + "</code></pre>")
        elif re.match(r"^### ", stripped):
            flush_paragraph()
            close_list()
            out.append("<h3>" + inline(stripped[4:]) + "</h3>")
        elif re.match(r"^## ", stripped):
            flush_paragraph()
            close_list()
            out.append("<h2>" + inline(stripped[3:]) + "</h2>")
        elif re.match(r"^# ", stripped):
            flush_paragraph()
            close_list()
            out.append("<h2>" + inline(stripped[2:]) + "</h2>")
        elif re.match(r"^[-*] ", stripped):
            flush_paragraph()
            if list_open != "ul":
                close_list()
                out.append("<ul>")
                list_open = "ul"
            out.append("<li>" + inline(stripped[2:]) + "</li>")
        elif re.match(r"^\d+\. ", stripped):
            flush_paragraph()
            if list_open != "ol":
                close_list()
                out.append("<ol>")
                list_open = "ol"
            out.append("<li>" + inline(re.sub(r"^\d+\. ", "", stripped)) + "</li>")
        elif stripped.startswith("> "):
            flush_paragraph()
            close_list()
            out.append("<blockquote><p>" + inline(stripped[2:]) + "</p></blockquote>")
        elif stripped == "":
            flush_paragraph()
            close_list()
        else:
            paragraph.append(stripped)
        i += 1
    flush_paragraph()
    close_list()
    return "\n".join(out)


def reading_time(body):
    return max(1, round(len(body.split()) / 200))


def date_label(date_str):
    parsed = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{parsed.day} {MONTHS[parsed.month - 1]} {parsed.year}"


def load_posts():
    posts = []
    for filename in sorted(os.listdir(POSTS_DIR)):
        if not filename.endswith(".md"):
            continue
        with open(os.path.join(POSTS_DIR, filename), encoding="utf-8") as handle:
            meta, body = parse_front_matter(handle.read())
        match = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$", filename)
        if match:
            date, slug = match.group(1), match.group(2)
        else:
            date = meta.get("date", datetime.now().strftime("%Y-%m-%d"))
            slug = re.sub(r"[^a-z0-9]+", "-", meta.get("title", filename).lower()).strip("-")
        posts.append({
            "title": meta.get("title", slug.replace("-", " ").title()),
            "description": meta.get("description", ""),
            "date": meta.get("date", date),
            "lang": meta.get("lang", "es"),
            "tags": [tag.strip() for tag in meta.get("tags", "").split(",") if tag.strip()],
            "slug": slug,
            "body": body,
        })
    posts.sort(key=lambda post: post["date"], reverse=True)
    return posts


def render_post(post):
    url = f"{SITE}/blog/{post['slug']}.html"
    tags_html = " ".join(f'<span class="tag">{esc(tag)}</span>' for tag in post["tags"])
    jsonld = BLOCK_JSONLD.format(
        title=post["title"].replace('"', "'"),
        description=post["description"].replace('"', "'"),
        date=post["date"],
        lang=post["lang"],
        author=AUTHOR,
        site=SITE,
        url=url,
    )
    page = POST_TEMPLATE.format(
        base="../",
        lang=post["lang"],
        home="Portafolio",
        blog="Blog",
        title=esc(post["title"]),
        description=esc(post["description"]),
        date_label=date_label(post["date"]),
        reading=reading_time(post["body"]),
        tags=tags_html,
        content=md_to_html(post["body"]),
        url=url,
        site=SITE,
        jsonld=jsonld,
        cta_text="¿Te sirvió este post o quieres algo así en tu equipo? Escríbeme y lo conversamos.",
        cta_label="Contacto",
        portfolio_label="Ver portafolio",
    )
    with open(os.path.join(BLOG_DIR, f"{post['slug']}.html"), "w", encoding="utf-8") as handle:
        handle.write(page)


def render_index(posts):
    cards = "\n".join(
        POST_CARD.format(
            url=f"{post['slug']}.html",
            title=esc(post["title"]),
            description=esc(post["description"]),
            date_label=date_label(post["date"]),
            reading=reading_time(post["body"]),
            tags_html=" ".join(f'<span class="tag">{esc(tag)}</span>' for tag in post["tags"]),
        )
        for post in posts
    )
    page = INDEX_TEMPLATE.format(cards=cards, site=SITE)
    with open(os.path.join(BLOG_DIR, "index.html"), "w", encoding="utf-8") as handle:
        handle.write(page)


def render_feed(posts):
    items = []
    for post in posts:
        url = f"{SITE}/blog/{post['slug']}.html"
        published = datetime.strptime(post["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        items.append(
            "    <item>\n"
            f"      <title>{esc(post['title'])}</title>\n"
            f"      <link>{url}</link>\n"
            f"      <guid>{url}</guid>\n"
            f"      <description>{esc(post['description'])}</description>\n"
            f"      <pubDate>{format_datetime(published)}</pubDate>\n"
            "    </item>"
        )
    build_date = format_datetime(datetime.now(timezone.utc))
    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        "    <title>Blog de Julian Urrego — IA aplicada y datos</title>\n"
        f"    <link>{SITE}/blog/</link>\n"
        "    <description>IA aplicada, marketing science y datos para negocios en LATAM.</description>\n"
        "    <language>es</language>\n"
        f"    <lastBuildDate>{build_date}</lastBuildDate>\n"
        f'    <atom:link href="{SITE}/blog/feed.xml" rel="self" type="application/rss+xml" />\n'
        + "\n".join(items)
        + "\n  </channel>\n</rss>\n"
    )
    with open(os.path.join(BLOG_DIR, "feed.xml"), "w", encoding="utf-8") as handle:
        handle.write(feed)


def render_sitemap(posts):
    today = datetime.now().strftime("%Y-%m-%d")
    latest = posts[0]["date"] if posts else today
    urls = [
        ("/", latest, "weekly", "1.0"),
        ("/blog/", latest, "weekly", "0.8"),
    ]
    for post in posts:
        urls.append((f"/blog/{post['slug']}.html", post["date"], "monthly", "0.7"))
    entries = "\n".join(
        "  <url>\n"
        f"    <loc>{SITE}{path}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n"
        f"    <changefreq>{freq}</changefreq>\n"
        f"    <priority>{priority}</priority>\n"
        "  </url>"
        for path, lastmod, freq, priority in urls
    )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n</urlset>\n"
    )
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as handle:
        handle.write(sitemap)


def render_home_section(posts):
    path = os.path.join(ROOT, "index.html")
    with open(path, encoding="utf-8") as handle:
        page = handle.read()
    cards = "\n".join(
        POST_CARD.format(
            url=f"blog/{post['slug']}.html",
            title=esc(post["title"]),
            description=esc(post["description"]),
            date_label=date_label(post["date"]),
            reading=reading_time(post["body"]),
            tags_html=" ".join(f'<span class="tag">{esc(tag)}</span>' for tag in post["tags"]),
        )
        for post in posts[:3]
    )
    updated = re.sub(
        r"(<!-- POSTS:START -->)(.*?)(<!-- POSTS:END -->)",
        lambda match: match.group(1) + "\n" + cards + "\n        " + match.group(3),
        page,
        flags=re.S,
    )
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(updated)


def main():
    os.makedirs(BLOG_DIR, exist_ok=True)
    posts = load_posts()
    for post in posts:
        render_post(post)
    render_index(posts)
    render_feed(posts)
    render_sitemap(posts)
    render_home_section(posts)
    print(f"OK · {len(posts)} posts · blog/ + feed.xml + sitemap.xml + home actualizados")


if __name__ == "__main__":
    main()
