#!/usr/bin/env python3
"""Regenerate privacy.html and terms.html from the copy inside index.html.

Why these pages exist as static HTML
------------------------------------
The site is a single-page app: index.html holds every page and support.js
decides which one to show from `location.hash`. That is fine for a human
browsing the site, but the privacy policy URL is also read by machines —
Google Play validates the policy URL you enter in the Data safety form, and
App Review opens it cold — and a page whose text only appears after JavaScript
runs can look empty to them. So /privacy and /terms are real documents with
the text in the HTML, and the SPA keeps its own copies for in-site navigation.

Two copies means drift, which is what this script is for: edit the legal copy
in index.html as usual, then run

    python3 tools/build-legal-pages.py

and commit all three files together.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

PAGES = [
    (
        "isPrivacy",
        "privacy",
        "Privacy policy",
        "How Sponte collects, uses and stores your information, including "
        "health and fitness data.",
    ),
    (
        "isTerms",
        "terms",
        "Terms of service",
        "The terms that govern your use of Sponte.",
    ),
]

TEMPLATE = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title} — Sponte</title>
    <meta name="description" content="{desc}" />
    <link rel="canonical" href="https://self-iterate.com/{slug}" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="" />
    <link
      href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&display=swap"
      rel="stylesheet"
    />
    <style>
      :root {{
        --bg: #060606;
        --bg2: #101010;
        --ink: #f5f5f0;
        --sec: #8a8a82;
        --line: rgba(255, 255, 255, 0.14);
        --brand: #2294fb;
      }}
      @media (prefers-color-scheme: light) {{
        :root {{
          --bg: #f5f5f0;
          --bg2: #ecece4;
          --ink: #141414;
          --sec: #6e6e64;
          --line: rgba(0, 0, 0, 0.16);
        }}
      }}
      * {{
        box-sizing: border-box;
      }}
      body {{
        margin: 0;
        background: var(--bg);
        color: var(--ink);
        font-family: Archivo, -apple-system, BlinkMacSystemFont, "Segoe UI",
          Roboto, sans-serif;
        -webkit-font-smoothing: antialiased;
      }}
      main {{
        padding: 64px 24px 72px !important;
      }}
      h1 {{
        margin-top: 20px !important;
      }}
      .legal-doc {{
        margin-top: 48px;
        max-width: 760px;
      }}
      .legal-doc .company {{
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.6px;
        text-transform: uppercase;
        color: var(--sec);
        margin: 0 0 8px;
      }}
      .legal-doc h2 {{
        font-size: 20px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        margin: 36px 0 12px;
        padding-top: 28px;
        border-top: 1px solid var(--line);
      }}
      .legal-doc p {{
        font-size: 15px;
        line-height: 1.65;
        color: var(--sec);
        margin: 0 0 14px;
      }}
      .legal-doc a {{
        color: var(--brand);
      }}
      .legal-doc .caps {{
        font-weight: 600;
        color: var(--ink);
        font-size: 13.5px;
      }}
      footer {{
        max-width: 760px;
        margin: 0 auto;
        padding: 0 24px 72px;
        border-top: 1px solid var(--line);
        display: flex;
        gap: 18px;
        flex-wrap: wrap;
        font-size: 13px;
      }}
      footer a {{
        color: var(--sec);
        padding-top: 20px;
      }}
    </style>
  </head>
  <body>
{body}
    <footer>
      <a href="/">Sponte</a>
      <a href="/privacy">Privacy policy</a>
      <a href="/terms">Terms of service</a>
      <a href="/support">Support</a>
      <a href="/delete-account">Delete your account</a>
    </footer>
  </body>
</html>
"""


def extract(src: str, var: str) -> str:
    """The <main> element inside the SPA's `sc-if` block for one page."""
    start = src.index(f'<sc-if value="{{{{ {var} }}}}">')
    mstart = src.index("<main", start)
    mend = src.index("</main>", mstart) + len("</main>")
    body = src[mstart:mend]
    # Drop the shell's own page padding; the standalone page sets its own.
    body = body.replace(
        '<main style="max-width: 1240px; margin: 0 auto; padding: 80px 32px">',
        '<main style="max-width: 1240px; margin: 0 auto">',
    )
    leftovers = re.findall(r"\{\{.*?\}\}", body)
    if leftovers:
        raise SystemExit(
            f"{var}: SPA template syntax in the extracted copy {leftovers}; "
            "a standalone page cannot render it."
        )
    return body


def main() -> None:
    src = INDEX.read_text(encoding="utf8")
    for var, slug, title, desc in PAGES:
        body = extract(src, var)
        out = ROOT / f"{slug}.html"
        out.write_text(
            TEMPLATE.format(title=title, desc=desc, slug=slug, body=body),
            encoding="utf8",
        )
        print(f"✓ {slug}.html ({len(body):,} bytes of document)")


if __name__ == "__main__":
    main()
