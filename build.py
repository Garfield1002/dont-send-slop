#!/usr/bin/env python3
"""Build essay.html from essay.md (stdlib only). With --pdf, also print
it to worth-their-time.pdf using headless Chromium.

Supported markdown: a setext title (underlined with ===), an optional
'>' epigraph right after it (last line '— Source' is the attribution),
blank-line separated paragraphs, *emphasis*, [links](url). Straight quotes become curly quotes.
"""
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "essay.md"
OUT = ROOT / "essay.html"
PDF = ROOT / "worth-their-time.pdf"
DESCRIPTION = "A short essay on respecting other people’s time when you write to them."

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta name="twitter:card" content="summary">
<link rel="preload" href="fonts/CrimsonPro-Regular.woff2" as="font" type="font/woff2" crossorigin>
<style>
  @font-face {{
    font-family: "Crimson Pro";
    src: url("fonts/CrimsonPro-Regular.woff2") format("woff2");
    font-style: normal;
    font-weight: 400;
    font-display: swap;
  }}
  @font-face {{
    font-family: "Crimson Pro";
    src: url("fonts/CrimsonPro-Italic.woff2") format("woff2");
    font-style: italic;
    font-weight: 400;
    font-display: swap;
  }}
  html {{ background: #fbf8f1; color: #1f1d1a; }}
  body {{
    max-width: 28em;            /* ~65-70 characters in Crimson Pro */
    margin: 0 auto;
    padding: 5rem 1.5rem 4rem;
    font-family: "Crimson Pro", Georgia, serif;
    font-size: 1.3rem;          /* ~21px */
    line-height: 1.5;
    font-kerning: normal;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
  }}
  h1 {{
    font-size: 2em;
    font-weight: 400;
    line-height: 1.2;
    text-align: center;
    text-decoration: underline;
    text-decoration-thickness: 1px;
    text-underline-offset: 0.18em;
    margin: 0 0 2rem;
  }}
  .epigraph {{
    max-width: 24em;
    margin: 0 auto 2.5rem;
  }}
  .epigraph blockquote {{ margin: 0; font-style: italic; }}
  .epigraph blockquote p {{ margin: 0; text-align: left; }}
  .epigraph figcaption {{ text-align: right; margin-top: 0.25em; }}
  p {{
    margin: 0 0 1em;
    text-align: justify;
    hyphens: auto;
    text-wrap: pretty;
  }}
  a {{ color: inherit; text-decoration: none; }}
  .flourish {{
    text-align: center;
    font-size: 1.6em;
    line-height: 1;
    margin: 2rem 0 0;
  }}
  @media (max-width: 36rem) {{
    body {{ font-size: 1.15rem; padding: 2.5rem 1.25rem 3rem; }}
    h1 {{ margin-bottom: 1.5rem; }}
    p {{ text-align: left; }}
  }}
  @page {{ size: A4; margin: 25mm 20mm; }}
  @media print {{
    html {{ background: #fff; color: #000; }}
    body {{ max-width: 28em; padding: 0; font-size: 12pt; }}
    h1 {{ margin-bottom: 1.5rem; }}
    p, .epigraph {{ break-inside: avoid; }}
  }}
</style>
</head>
<body>
<h1>{title}</h1>
{epigraph}
{body}

<div class="flourish" aria-hidden="true">&#x2767;</div>
</body>
</html>
"""


def inline(text: str) -> str:
    text = re.sub(r'"([^"]*)"', "“\\1”", text)  # "..." -> “...”
    text = text.replace("'", "’")  # apostrophes -> ’
    text = html.escape(text, quote=False)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)


def epigraph(block: str) -> str:
    """A '>' block; a last line starting with an em dash is the attribution."""
    lines = [re.sub(r"^>\s?", "", l).strip() for l in block.splitlines()]
    source = lines.pop()[1:].strip() if len(lines) > 1 and lines[-1].startswith("—") else None
    quote = f"<blockquote><p>{inline(' '.join(lines))}</p></blockquote>"
    cap = f"\n<figcaption>— {inline(source)}</figcaption>" if source else ""
    return f'\n<figure class="epigraph">\n{quote}{cap}\n</figure>\n'


def build() -> None:
    blocks = re.split(r"\n\s*\n", SRC.read_text(encoding="utf-8").strip())
    head = blocks.pop(0).splitlines()
    if len(head) != 2 or not re.fullmatch(r"=+", head[1].strip()):
        raise SystemExit("essay.md must start with a title underlined by ===")
    title = inline(head[0].strip())
    epi = epigraph(blocks.pop(0)) if blocks and blocks[0].startswith(">") else ""
    paras = [f"<p>{inline(b.strip())}</p>" for b in blocks if b.strip()]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(TEMPLATE.format(title=title, description=DESCRIPTION, epigraph=epi,
                                   body="\n\n".join(paras)), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


def pdf() -> None:
    browser = next((b for b in ("chromium-browser", "chromium", "google-chrome", "chrome")
                    if shutil.which(b)), None)
    if not browser:
        raise SystemExit("--pdf needs Chromium or Chrome on PATH")
    subprocess.run([browser, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={PDF}", OUT.resolve().as_uri()],
                   check=True, stderr=subprocess.DEVNULL)
    print(f"wrote {PDF.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
    if "--pdf" in sys.argv[1:]:
        pdf()
