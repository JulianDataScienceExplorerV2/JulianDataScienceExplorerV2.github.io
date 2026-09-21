#!/usr/bin/env python3
import html
import json
import os
import re
from datetime import datetime, timezone
from email.utils import format_datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, "posts")
BLOG_DIR = os.path.join(ROOT, "blog")
SITE = "https://juliandatascienceexplorerv2.github.io"
AUTHOR = "Julian David Urrego Lancheros"
LANGS = ["es", "en", "pt"]
LANG_LABELS = {"es": "🇨🇴 ES", "en": "🇺🇸 EN", "pt": "🇧🇷 PT"}
LANG_NAMES = {"es": "Español", "en": "English", "pt": "Português"}
MONTHS = {
    "es": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"],
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "pt": ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"],
}
UI = {
    "es": {
        "home": "Portafolio", "blog": "Blog", "back": "← Volver al blog",
        "reading": "min de lectura", "contact": "Contacto", "portfolio": "Ver portafolio",
        "cta": "¿Te sirvió este post o quieres algo así en tu equipo? Escríbeme y lo conversamos.",
        "index_title": "IA aplicada y datos para negocios",
        "index_desc": "Guías prácticas, experimentos y aprendizajes sobre IA, automatización y analítica en LATAM. Con ejemplos reales, no teoría.",
    },
    "en": {
        "home": "Portfolio", "blog": "Blog", "back": "← Back to blog",
        "reading": "min read", "contact": "Contact me", "portfolio": "View portfolio",
        "cta": "Did this post help you, or do you want something like this for your team? Reach out and let's talk.",
        "index_title": "Applied AI and data for business",
        "index_desc": "Practical guides, experiments, and lessons on AI, automation, and analytics in LATAM. Real examples, not theory.",
    },
    "pt": {
        "home": "Portfólio", "blog": "Blog", "back": "← Voltar ao blog",
        "reading": "min de leitura", "contact": "Fale comigo", "portfolio": "Ver portfólio",
        "cta": "Este post te ajudou ou você quer algo assim na sua equipe? Me escreve e conversamos.",
        "index_title": "IA aplicada e dados para negócios",
        "index_desc": "Guias práticos, experimentos e aprendizados sobre IA, automação e analytics na América Latina. Com exemplos reais, sem teoria.",
    },
}

POST_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title} — Julian David Urrego Lancheros</title>
<meta name="description" content="{description}" />
<meta name="theme-color" content="#07070a" />
<link rel="canonical" href="{url}" />
{alternates}
<meta property="og:type" content="article" />
<meta property="og:url" content="{url}" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{description}" />
<meta property="og:image" content="{site}/og-image.png" />
<meta property="og:locale" content="{locale}" />
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
    <p class="kicker"><a href="{base}blog/" style="color:inherit;text-decoration:none">{back}</a></p>
    <h1 class="sec-h" style="font-size:2rem;line-height:1.2">{title}</h1>
    <p class="post-meta">{date_label} · {reading} {reading_label} · {tags} <span class="lang-switch">{lang_links}</span></p>
    <article class="post">
{content}
    </article>
    <div class="dl" style="margin-top:3rem">
      <p style="font-size:14px;color:var(--text-2);line-height:1.7">
        {cta}
      </p>
      <div style="display:flex;gap:.75rem;flex-wrap:wrap">
        <a class="cta1" href="{base}#contact">{contact}</a>
        <a class="cta2" href="{base}">{portfolio}</a>
      </div>
    </div>
  </div>
</div>

<footer>Julian David Urrego Lancheros &mdash; <span class="hi">juliandatascienceexplorerv2.github.io</span></footer>
{lang_suggest}
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
    <p class="sec-s">Guías prácticas, experimentos y aprendizajes sobre IA, automatización y analítica en LATAM. Con ejemplos reales, no teoría. Disponible en <strong>español</strong>, <strong>english</strong> and <strong>português</strong>.</p>
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
          <div class="cmeta">{lang_badges}<span class="ctime">{date_label}</span></div>
        </div>
        <p class="cname">{title}</p>
        <p class="cdesc">{description}</p>
        <div class="cfoot"><div class="tags">{tags_html}</div><span class="ctime">{reading} {reading_label}</span></div>
      </a>
"""

BLOCK_JSONLD = """{{"@context":"https://schema.org","@type":"BlogPosting","headline":"{title}","description":"{description}","datePublished":"{date}","dateModified":"{date}","inLanguage":"{lang}","author":{{"@type":"Person","name":"{author}","url":"{site}"}},"publisher":{{"@type":"Person","name":"{author}"}},"mainEntityOfPage":"{url}","image":"{site}/og-image.png"}}"""

SUGGEST = {
    "es": {"label": "Este artículo también está disponible en español", "cta": "Leer en español 🇨🇴"},
    "en": {"label": "This post is also available in English", "cta": "Read in English 🇺🇸"},
    "pt": {"label": "Este post também está disponível em português", "cta": "Ler em português 🇧🇷"},
}

LANG_SUGGEST_SCRIPT = r"""<div id="langSuggest" class="lang-suggest" hidden>
  <span id="langSuggestText"></span>
  <a id="langSuggestLink" href="#"></a>
  <button type="button" aria-label="Cerrar" onclick="this.parentNode.hidden = true">&times;</button>
</div>
<script>
(function () {
  var data = __LINKS__;
  var current = "__CURRENT__";
  var stored = null;
  try { stored = localStorage.getItem("lang") } catch (error) {}
  var pick = stored;
  if (!pick) {
    var candidates = (navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || ""]).map(function (code) { return code.toLowerCase() });
    for (var i = 0; i < candidates.length; i++) {
      var code = candidates[i];
      if (code.indexOf("es") === 0) { pick = "es"; break }
      if (code.indexOf("pt") === 0) { pick = "pt"; break }
      if (code.indexOf("en") === 0) { pick = "en"; break }
    }
  }
  if (!pick) {
    var tz = "";
    try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "" } catch (error) {}
    pick = /^America\/(Sao_Paulo|Bahia|Fortaleza|Recife|Belem|Manaus|Cuiaba|Campo_Grande|Maceio|Joao_Pessoa|Araguaina|Porto_Velho|Rio_Branco|Boa_Vista|Noronha|Santarem)$/.test(tz) ? "pt" : (tz.indexOf("America/") === 0 ? "es" : "en");
  }
  if (pick && pick !== current && data[pick]) {
    document.getElementById("langSuggestText").textContent = data[pick].label;
    var link = document.getElementById("langSuggestLink");
    link.href = data[pick].url;
    link.textContent = data[pick].cta;
    document.getElementById("langSuggest").hidden = false;
  }
})();
</script>"""


def parse_front_matter(text):
    meta = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    key, _, value = line.partition(":")
                    val = value.strip()
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    meta[key.strip()] = val
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
        image = re.match(r"^!\[([^\]]*)\]\(([^)\s]+)\)$", stripped)
        if stripped.startswith("```"):
            flush_paragraph()
            close_list()
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            out.append("<pre><code>" + "\n".join(code) + "</code></pre>")
        elif image:
            flush_paragraph()
            close_list()
            alt, src = image.group(1), image.group(2)
            caption = f"<figcaption>{alt}</figcaption>" if alt else ""
            out.append(f'<figure><img src="{src}" alt="{alt}" loading="lazy" decoding="async" />{caption}</figure>')
        elif stripped.startswith("|") and stripped.endswith("|"):
            flush_paragraph()
            close_list()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                rows.append([cell.strip() for cell in lines[i].strip().strip("|").split("|")])
                i += 1
            i -= 1
            if len(rows) >= 2 and all(set(cell) <= set("-: ") and cell for cell in rows[1]):
                head = "".join(f"<th>{inline(cell)}</th>" for cell in rows[0])
                body = "".join("<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>" for row in rows[2:])
                out.append(f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>")
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
        elif stripped.startswith(("&gt; ", "> ")):
            flush_paragraph()
            close_list()
            quote_lines = []
            while i < len(lines) and (lines[i].strip().startswith(("&gt; ", "> ")) or lines[i].strip() in ("&gt;", ">")):
                l_str = lines[i].strip()
                if l_str.startswith("&gt; "):
                    quote_lines.append(l_str[5:])
                elif l_str.startswith("> "):
                    quote_lines.append(l_str[2:])
                else:
                    quote_lines.append("")
                i += 1
            i -= 1
            inner_paras = []
            curr = []
            for ql in quote_lines:
                if ql == "":
                    if curr:
                        inner_paras.append("<p>" + "<br />".join(inline(c) for c in curr) + "</p>")
                        curr = []
                else:
                    curr.append(ql)
            if curr:
                inner_paras.append("<p>" + "<br />".join(inline(c) for c in curr) + "</p>")
            out.append("<blockquote>" + "".join(inner_paras) + "</blockquote>")
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


def date_label(date_str, lang):
    parsed = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{parsed.day} {MONTHS[lang][parsed.month - 1]} {parsed.year}"


def load_groups():
    groups = {}
    for filename in sorted(os.listdir(POSTS_DIR)):
        match = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+?)(?:\.(es|en|pt))?\.md$", filename)
        if not match:
            continue
        file_date, slug, lang = match.group(1), match.group(2), match.group(3) or "es"
        with open(os.path.join(POSTS_DIR, filename), encoding="utf-8") as handle:
            meta, body = parse_front_matter(handle.read())
        lang = meta.get("lang", lang)
        groups.setdefault(slug, {"slug": slug, "date": meta.get("date", file_date), "translations": {}})
        groups[slug]["translations"][lang] = {
            "title": meta.get("title", slug.replace("-", " ").title()),
            "description": meta.get("description", ""),
            "date": meta.get("date", file_date),
            "tags": [tag.strip() for tag in meta.get("tags", "").split(",") if tag.strip()],
            "body": body,
        }
    ordered = sorted(groups.values(), key=lambda group: group["date"], reverse=True)
    for group in ordered:
        if "es" in group["translations"]:
            group["default"] = "es"
        else:
            group["default"] = next(iter(group["translations"]))
    return ordered


def post_url(group, lang):
    if lang == group["default"]:
        return f"{SITE}/blog/{group['slug']}.html"
    return f"{SITE}/blog/{group['slug']}.{lang}.html"


def local_url(group, lang):
    if lang == group["default"]:
        return f"{group['slug']}.html"
    return f"{group['slug']}.{lang}.html"


def extract_faqs(body):
    faqs = []
    pattern = re.compile(r"^###\s+([¿\?].+?)\s*\n+(.+?)(?=\n+###|\n+##|\Z)", re.M | re.S)
    for match in pattern.finditer(body):
        q = match.group(1).strip()
        ans = match.group(2).strip()
        clean_ans = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", ans)
        clean_ans = re.sub(r"[*_`]", "", clean_ans).replace("\n", " ").strip()
        if len(clean_ans) > 20:
            faqs.append((q, clean_ans))
    return faqs


def render_post(group, lang):
    post = group["translations"][lang]
    ui = UI[lang]
    url = post_url(group, lang)
    tags_html = " ".join(f'<span class="tag">{esc(tag)}</span>' for tag in post["tags"])
    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{code}" href="{post_url(group, code)}" />'
        for code in LANGS if code in group["translations"]
    )
    alternates += f'\n<link rel="alternate" hreflang="x-default" href="{post_url(group, group["default"])}" />'
    lang_link_parts = []
    for code in LANGS:
        if code in group["translations"]:
            active = ' class="active"' if code == lang else ""
            lang_link_parts.append(f'<a href="{local_url(group, code)}"{active}>{LANG_LABELS[code]}</a>')
    lang_links = " · ".join(lang_link_parts)
    
    faqs = extract_faqs(post["body"])
    posting_entity = {
        "@type": "BlogPosting",
        "headline": post["title"],
        "description": post["description"],
        "datePublished": post["date"],
        "dateModified": post["date"],
        "inLanguage": lang,
        "author": {
            "@type": "Person",
            "name": AUTHOR,
            "url": SITE
        },
        "publisher": {
            "@type": "Person",
            "name": AUTHOR
        },
        "mainEntityOfPage": url,
        "image": f"{SITE}/og-image.png"
    }
    if faqs:
        faq_entity = {
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": a
                    }
                } for q, a in faqs
            ]
        }
        jsonld = json.dumps({"@context": "https://schema.org", "@graph": [posting_entity, faq_entity]}, ensure_ascii=False, indent=2)
    else:
        jsonld = json.dumps({"@context": "https://schema.org", **posting_entity}, ensure_ascii=False, indent=2)

    locales = {"es": "es_CO", "en": "en_US", "pt": "pt_BR"}
    links = {
        code: {"url": local_url(group, code), "label": SUGGEST[code]["label"], "cta": SUGGEST[code]["cta"]}
        for code in group["translations"]
    }
    lang_suggest = LANG_SUGGEST_SCRIPT.replace("__LINKS__", json.dumps(links, ensure_ascii=False)).replace("__CURRENT__", lang)
    page = POST_TEMPLATE.format(
        base="../",
        lang=lang,
        home=ui["home"],
        blog=ui["blog"],
        back=ui["back"],
        title=esc(post["title"]),
        description=esc(post["description"]),
        date_label=date_label(post["date"], lang),
        reading=reading_time(post["body"]),
        reading_label=ui["reading"],
        tags=tags_html,
        lang_links=lang_links,
        alternates=alternates,
        locale=locales.get(lang, "es_CO"),
        content=md_to_html(post["body"]),
        url=url,
        site=SITE,
        jsonld=jsonld,
        cta=ui["cta"],
        contact=ui["contact"],
        portfolio=ui["portfolio"],
        lang_suggest=lang_suggest,
    )
    with open(os.path.join(BLOG_DIR, local_url(group, lang)), "w", encoding="utf-8") as handle:
        handle.write(page)


def render_index(groups):
    cards = []
    for group in groups:
        post = group["translations"][group["default"]]
        badges = " ".join(
            f'<span class="pinbadge">{LANG_LABELS[code]}</span>' for code in LANGS if code in group["translations"]
        )
        cards.append(
            POST_CARD.format(
                url=local_url(group, group["default"]),
                title=esc(post["title"]),
                description=esc(post["description"]),
                date_label=date_label(group["date"], "es"),
                reading=reading_time(post["body"]),
                reading_label=UI["es"]["reading"],
                tags_html=" ".join(f'<span class="tag">{esc(tag)}</span>' for tag in post["tags"]),
                lang_badges=badges,
            )
        )
    page = INDEX_TEMPLATE.format(cards="\n".join(cards), site=SITE)
    with open(os.path.join(BLOG_DIR, "index.html"), "w", encoding="utf-8") as handle:
        handle.write(page)


def render_feed(groups):
    items = []
    for group in groups:
        post = group["translations"][group["default"]]
        url = post_url(group, group["default"])
        published = datetime.strptime(group["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
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


def render_sitemap(groups):
    today = datetime.now().strftime("%Y-%m-%d")
    latest = groups[0]["date"] if groups else today
    urls = [
        ("/", latest, "weekly", "1.0"),
        ("/blog/", latest, "weekly", "0.8"),
    ]
    for group in groups:
        for lang in LANGS:
            if lang in group["translations"]:
                path = f"/blog/{local_url(group, lang)}"
                urls.append((path, group["date"], "monthly", "0.7"))
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


def render_home_section(groups):
    path = os.path.join(ROOT, "index.html")
    with open(path, encoding="utf-8") as handle:
        page = handle.read()
    cards = []
    for group in groups[:3]:
        post = group["translations"][group["default"]]
        badges = " ".join(
            f'<span class="pinbadge">{LANG_LABELS[code]}</span>' for code in LANGS if code in group["translations"]
        )
        cards.append(
            POST_CARD.format(
                url=f"blog/{local_url(group, group['default'])}",
                title=esc(post["title"]),
                description=esc(post["description"]),
                date_label=date_label(group["date"], "es"),
                reading=reading_time(post["body"]),
                reading_label=UI["es"]["reading"],
                tags_html=" ".join(f'<span class="tag">{esc(tag)}</span>' for tag in post["tags"]),
                lang_badges=badges,
            )
        )
    updated = re.sub(
        r"(<!-- POSTS:START -->)(.*?)(<!-- POSTS:END -->)",
        lambda match: match.group(1) + "\n" + "\n".join(cards) + "\n        " + match.group(3),
        page,
        flags=re.S,
    )
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(updated)


def main():
    os.makedirs(BLOG_DIR, exist_ok=True)
    groups = load_groups()
    for group in groups:
        for lang in LANGS:
            if lang in group["translations"]:
                render_post(group, lang)
    render_index(groups)
    render_feed(groups)
    render_sitemap(groups)
    render_home_section(groups)
    total = sum(len(group["translations"]) for group in groups)
    print(f"OK · {len(groups)} posts · {total} versiones (ES/EN/PT) · blog/ + feed + sitemap + home")


if __name__ == "__main__":
    main()
