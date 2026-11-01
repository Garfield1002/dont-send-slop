#!/usr/bin/env python3
"""Build site/index.html from essay.md (stdlib only).

Supported markdown: a setext title (underlined with ===), blank-line
separated paragraphs, *emphasis*. Straight quotes become curly quotes.
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "essay.md"
OUT = ROOT / "site" / "index.html"

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="A short essay on why sending unreviewed, low-effort messages is rude.">
<style>
  html {{ background: #fff; color: #000; }}
  body {{
    max-width: 80ch;
    margin: 6rem auto 5rem;
    padding: 0 1.5rem;
    font-family: Charter, "Bitstream Charter", XCharter, "Iowan Old Style",
                 "Palatino Linotype", Palatino, Georgia, serif;
    font-size: 1.2rem;
    line-height: 1.6;
    font-kerning: normal;
    font-variant-ligatures: common-ligatures;
    font-variant-numeric: oldstyle-nums;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
  }}
  h1 {{
    font-size: 2.2rem;
    font-weight: normal;
    letter-spacing: 0.01em;
    text-align: center;
    text-decoration: underline;
    text-decoration-thickness: 1px;
    text-underline-offset: 0.25em;
    margin: 0 0 3rem;
  }}
  p {{
    margin: 0;
    text-align: justify;
    hyphens: auto;
    text-wrap: pretty;
  }}
  p + p {{ text-indent: 1.5em; }}
  p:first-of-type::first-line {{ font-variant-caps: small-caps; letter-spacing: 0.03em; }}
  em {{ font-style: italic; }}
  .flourish {{
    text-align: center;
    font-size: 1.5rem;
    line-height: 1;
    margin-top: 2.5rem;
  }}
  @media (max-width: 40rem) {{
    body {{ margin-top: 3rem; font-size: 1.1rem; }}
    p {{ text-align: left; }}
  }}
</style>
</head>
<body>
<h1>{title}</h1>

{body}

<div class="flourish" aria-hidden="true">&#x2766;</div>
</body>
</html>
"""


def inline(text: str) -> str:
    text = re.sub(r'"([^"]*)"', "“\\1”", text)  # "..." -> “...”
    text = text.replace("'", "’")  # apostrophes -> ’
    text = html.escape(text, quote=False)
    return re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)


def build() -> None:
    blocks = re.split(r"\n\s*\n", SRC.read_text(encoding="utf-8").strip())
    head = blocks[0].splitlines()
    if len(head) < 2 or not re.fullmatch(r"=+", head[1].strip()):
        raise SystemExit("essay.md must start with a title underlined by ===")
    title = inline(head[0].strip())
    rest = ["\n".join(head[2:])] if head[2:] else []
    paras = [f"<p>{inline(b.strip())}</p>" for b in rest + blocks[1:] if b.strip()]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(TEMPLATE.format(title=title, body="\n\n".join(paras)), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
