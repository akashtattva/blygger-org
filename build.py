#!/usr/bin/env python3
"""
build.py — render content/*.md into dist/ static HTML via templates/page.html.

Install once:
    /opt/homebrew/bin/python3 -m pip install markdown --break-system-packages

Usage:
    /opt/homebrew/bin/python3 build.py
"""

import re
import shutil
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("markdown not installed.\nRun: /opt/homebrew/bin/python3 -m pip install markdown --break-system-packages")

from build_talk import build_talks

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
TEMPLATE = (ROOT / "templates" / "page.html").read_text("utf-8")
EXTENSIONS = ["extra", "toc", "sane_lists"]

FENCE_RE = re.compile(r"^(\s*)(```+)(.*)$")


def dedent_fenced_blocks(text: str) -> str:
    """Shift indented ``` fences (and their contents) out to column 0.

    Python-Markdown's fenced_code only recognizes a fence at column 0, so an
    example indented under a list item is not treated as code: its first line
    becomes inline code and the rest is parsed as markdown, which passes raw
    HTML/XML through into the page. That silently emitted a live
    `<blockquote class="blyg-transclusion">` on the published 0.1 spec page,
    and a `<head><title>` inside the body on 0.2's OPML example.

    Fixing this in the renderer rather than in the prose is deliberate: spec
    documents freeze (a superseded version receives no revisions, and dated
    snapshots are immutable), so their pages can only be corrected here.
    Relative indentation inside a block is preserved; a fence already at
    column 0 passes through untouched.
    """
    out: list[str] = []
    fence_indent: str | None = None
    for line in text.split("\n"):
        m = FENCE_RE.match(line)
        if fence_indent is None:
            if m:
                fence_indent = m.group(1)
                out.append(m.group(2) + m.group(3))
            else:
                out.append(line)
        elif m and m.group(1) == fence_indent:
            out.append(m.group(2) + m.group(3))
            fence_indent = None
        elif fence_indent and line.startswith(fence_indent):
            out.append(line[len(fence_indent):])
        else:
            out.append(line)
    return "\n".join(out)


def flatten_h2(tokens):
    out = []
    for tok in tokens:
        if tok["level"] == 2:
            out.append(tok)
        out.extend(flatten_h2(tok["children"]))
    return out


def render_markdown(md_path: Path):
    md = markdown.Markdown(extensions=EXTENSIONS, extension_configs={"toc": {"permalink": False}})
    content_html = md.convert(dedent_fenced_blocks(md_path.read_text("utf-8")))
    return content_html, flatten_h2(md.toc_tokens)


def rail_items(tokens, numbered: bool) -> str:
    lines = []
    for i, tok in enumerate(tokens):
        name = tok["name"]
        if numbered:
            m = re.match(r"(\d+)\.\s*(.+)", name)
            idx, label = (m.group(1), m.group(2)) if m else (str(i + 1), name)
        else:
            idx, label = f"{i + 1:02d}", name
        lines.append(
            f'      <li><span class="idx">{idx}</span><a href="#{tok["id"]}">{label}</a></li>'
        )
    return "\n".join(lines)


def build_page(md_path: Path, out_path: Path, title: str, description: str,
                prompt: str, rail_label: str, numbered_rail: bool):
    content_html, tokens = render_markdown(md_path)
    page = (
        TEMPLATE
        .replace("{{TITLE}}", title)
        .replace("{{DESCRIPTION}}", description)
        .replace("{{PROMPT}}", prompt)
        .replace("{{RAIL_LABEL}}", rail_label)
        .replace("{{RAIL_ITEMS}}", rail_items(tokens, numbered_rail))
        .replace("{{CONTENT}}", content_html)
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, "utf-8")
    print(f"  {md_path.relative_to(ROOT)}  ->  {out_path.relative_to(ROOT)}")


def first_heading(md_path: Path, fallback: str) -> str:
    for line in md_path.read_text("utf-8").splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def build_spec_pages():
    """Walk content/spec/ for every sync_spec.py-generated index.md — the
    index page itself, each version's latest revision, and any dated
    snapshots — and build each. Depth-driven since the tree shape is fixed
    (spec/, spec/{version}/, spec/{version}/{date}/), not content-driven."""
    spec_root = ROOT / "content" / "spec"
    if not spec_root.is_dir():
        return
    for md_path in sorted(spec_root.rglob("index.md")):
        parts = md_path.relative_to(spec_root).parent.parts
        if parts == (".",) or parts == ():
            parts = ()
        url_path = "spec/" + "/".join(parts)
        out_path = DIST / "spec" / Path(*parts) / "index.html" if parts else DIST / "spec" / "index.html"
        prompt = f"~/blygger.org/{url_path}" + ("" if url_path.endswith("/") else "/")

        if len(parts) == 0:
            title = first_heading(md_path, "Blygger Protocol — Specification Index")
            description = "Index of Blygger protocol spec versions and dated snapshots."
            rail_label, numbered_rail = "Versions", False
        elif len(parts) == 1:
            version = parts[0]
            title = first_heading(md_path, f"The Blygger Protocol — Version {version}")
            description = f"Normative specification of the Blygger protocol, version {version}."
            rail_label, numbered_rail = "Sections", True
        else:
            version, date = parts[0], parts[1]
            title = first_heading(md_path, f"The Blygger Protocol — Version {version} ({date} snapshot)")
            description = f"Blygger protocol version {version}, immutable snapshot from {date}."
            rail_label, numbered_rail = "Sections", True

        build_page(md_path, out_path, title=title, description=description,
                   prompt=prompt, rail_label=rail_label, numbered_rail=numbered_rail)


def build_notes_pages():
    """Walk content/notes/ for every sync_spec.py-generated index.md — the
    index page itself and each tn-{N}/ page. Depth-driven like build_spec_pages,
    but shallower (notes/, notes/tn-{N}/ — no dated-snapshot tier)."""
    notes_root = ROOT / "content" / "notes"
    if not notes_root.is_dir():
        return
    for md_path in sorted(notes_root.rglob("index.md")):
        parts = md_path.relative_to(notes_root).parent.parts
        if parts == (".",) or parts == ():
            parts = ()
        url_path = "notes/" + "/".join(parts)
        out_path = DIST / "notes" / Path(*parts) / "index.html" if parts else DIST / "notes" / "index.html"
        prompt = f"~/blygger.org/{url_path}" + ("" if url_path.endswith("/") else "/")

        if len(parts) == 0:
            title = first_heading(md_path, "Blygger Technical Notes")
            description = "Index of Blygger protocol technical notes — non-normative design-reasoning records."
            rail_label, numbered_rail = "Notes", False
        else:
            tn = parts[0]
            title = first_heading(md_path, f"Blygger Technical Note — {tn}")
            description = f"Blygger technical note {tn}: non-normative design-reasoning record."
            rail_label, numbered_rail = "Sections", True

        build_page(md_path, out_path, title=title, description=description,
                   prompt=prompt, rail_label=rail_label, numbered_rail=numbered_rail)


if __name__ == "__main__":
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    print("Building HTML...")
    build_page(
        ROOT / "content" / "overview.md",
        DIST / "index.html",
        title="Blygger — an AI-native, decentralized medium for writing in public",
        description="Blygger is a protocol for public writing: fragments, threads, "
                     "TK-transclusion, and versioning over static files and RSS.",
        prompt="~/blygger.org/blyg/",
        rail_label="On this page",
        numbered_rail=False,
    )
    # NOTE: written as ns/0.1.html (not ns/0.1/index.html) deliberately — the
    # namespace URI as it appears in feed xmlns attributes is exactly
    # "https://blygger.org/ns/0.1", no trailing slash, and Pages' clean-URL
    # mapping serves /ns/0.1 from ns/0.1.html with a direct 200. The
    # directory form would 308-redirect the canonical slashless spelling.
    build_page(
        ROOT / "content" / "ns" / "0.1" / "index.md",
        DIST / "ns" / "0.1.html",
        title="The blyg: XML Namespace — https://blygger.org/ns/0.1",
        description="Descriptive note on the Blygger XML namespace: what the "
                     "blyg: elements in a Blygger RSS feed mean, and where the "
                     "normative specification lives.",
        prompt="~/blygger.org/ns/0.1",
        rail_label="On this page",
        numbered_rail=False,
    )
    build_page(
        ROOT / "content" / "start" / "index.md",
        DIST / "start" / "index.html",
        title="Build a blyg — Blygger",
        description="Three ways into the Blygger medium: publish a feed you already have, "
                    "host the reference client, or build your own client from the spec.",
        prompt="~/blygger.org/start/",
        rail_label="On this page",
        numbered_rail=True,
    )
    # The ecosystem directory (session 26) — generated by sync_ecosystem.py from
    # ecosystem/projects.toml plus a live census of blygger.com's listings. Skipped
    # rather than fatal when absent, so a fresh checkout builds before the first sync.
    eco = ROOT / "content" / "ecosystem" / "index.md"
    if eco.exists():
        build_page(
            eco,
            DIST / "ecosystem" / "index.html",
            title="The Blygger ecosystem — clients, tools and integrations",
            description="Community-built Blygger clients, authoring tools, "
                        "integrations and mods, with a live census of which client "
                        "serves each blyg in the directory.",
            prompt="~/blygger.org/ecosystem/",
            rail_label="On this page",
            numbered_rail=False,
        )
    else:
        print("  (no content/ecosystem/index.md — run ./sync_ecosystem.py)")
    build_spec_pages()
    build_notes_pages()
    # Talks (session 21) are a third genre alongside normative text and technical
    # notes: slides + full narration, built from talks/<slug>/ rather than from
    # content/, because the source is structured (slides.yaml) not prose.
    build_talks(DIST, TEMPLATE, lambda md: markdown.markdown(md, extensions=EXTENSIONS))

    shutil.copyfile(ROOT / "site.css", DIST / "site.css")
    print("  site.css  ->  dist/site.css")
    print("Done.")
