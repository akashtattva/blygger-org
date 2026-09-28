#!/usr/bin/env python3
"""
sync_spec.py — the only writer of content/spec/. Publishes the canonical spec
from the sibling blygger-spec checkout into this site's content tree.

Source of truth: ../blygger-spec/docs/protocol-v{X.Y}.md, one document per
protocol version (decision #23). Never hand-edit files under content/spec/ —
edit canonical there and rerun this script.

Usage:
    /opt/homebrew/bin/python3 sync_spec.py            # latest mode: every version (default)
    /opt/homebrew/bin/python3 sync_spec.py snapshot    # cut a dated snapshot of the living version
    /opt/homebrew/bin/python3 sync_spec.py snapshot --version 0.1

See docs/spec-publishing-plan.md (blygger-spec repo) for the full design.
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
SPEC_REPO = ROOT / ".." / "blygger-spec"
CONTENT_SPEC = ROOT / "content" / "spec"
NOTES_DIR = SPEC_REPO / "docs" / "notes"
CONTENT_NOTES = ROOT / "content" / "notes"

# Per-version status. Two forms (decision #23, spec-publishing-plan.md §6):
#   "DRAFT"                  — a version still receiving revisions.
#   ("SUPERSEDED", "0.2")    — frozen; a higher-numbered document took over.
# Publishing version N+1 means: add its row here as DRAFT, add its canonical
# file below, and flip version N to ("SUPERSEDED", "N+1") in the same change.
# The successor drives both the index row and the forward-linking banner on
# the superseded version's latest page. Dated snapshots are never bannered —
# immutability outranks supersession.
SPEC_VERSIONS = {
    "0.1": ("SUPERSEDED", "0.2"),
    "0.2": ("SUPERSEDED", "0.3"),
    "0.3": "DRAFT",
}
CANONICAL_FILES = {
    "0.1": SPEC_REPO / "docs" / "protocol-v0.1.md",
    "0.2": SPEC_REPO / "docs" / "protocol-v0.2.md",
    "0.3": SPEC_REPO / "docs" / "protocol-v0.3.md",
}

SITE_ORIGIN = "https://blygger.org"
GITHUB_REPO = "blygger/blygger-spec"
GITHUB_URL = f"https://github.com/{GITHUB_REPO}"
STUDIO_REPO = "blygger/blygger-studio"
STUDIO_URL = f"https://github.com/{STUDIO_REPO}"

MARKER_BEGIN = "<!-- spec-links:begin -->"
MARKER_END = "<!-- spec-links:end -->"
BULLET_RE = re.compile(r"^- \*\*([^:]+):\*\*\s?(.*)$")

NOTE_FILENAME_RE = re.compile(r"^tn-(\d+)-(.+)\.md$")
NOTE_TITLE_RE = re.compile(r"^#\s*TN-\d+\s*—\s*(.+)$")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
SUPERSEDED_RE = re.compile(r"superseded by (TN-\d+)", re.IGNORECASE)


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def sorted_versions(newest_first: bool = True) -> list[str]:
    return sorted(SPEC_VERSIONS, key=version_key, reverse=newest_first)


def status_of(version: str) -> tuple[str, str | None]:
    """(status, superseding version or None) — normalizes the two SPEC_VERSIONS forms."""
    entry = SPEC_VERSIONS[version]
    return entry if isinstance(entry, tuple) else (entry, None)


def living_version() -> str:
    """The highest-numbered version — the living document by definition (decision #23)."""
    return max(SPEC_VERSIONS, key=version_key)


def run(*args: str, cwd: Path) -> str:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def spec_repo_sha() -> str:
    return run("git", "rev-parse", "--short", "HEAD", cwd=SPEC_REPO)


def spec_repo_is_dirty() -> bool:
    return bool(run("git", "status", "--porcelain", cwd=SPEC_REPO))


def spec_repo_head_is_pushed() -> bool:
    try:
        local = run("git", "rev-parse", "HEAD", cwd=SPEC_REPO)
        upstream = run("git", "rev-parse", "@{u}", cwd=SPEC_REPO)
    except subprocess.CalledProcessError:
        return False
    return local == upstream


def existing_snapshots(version: str) -> list[str]:
    """Dated snapshot dirs for a version, ascending (oldest first). Stateless — derived by globbing."""
    version_dir = CONTENT_SPEC / version
    if not version_dir.is_dir():
        return []
    dates = [p.name for p in version_dir.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.name)]
    return sorted(dates)


def rewrite_links_block(canonical_text: str, this_version_url: str, latest_url: str, previous_url: str | None) -> str:
    """Surgically replace This/Latest/Previous version bullets; pass every other bullet
    (XML namespace, Source of truth, Reference implementation, License, ...) through verbatim."""
    m = re.search(rf"{re.escape(MARKER_BEGIN)}\n(.*?)\n{re.escape(MARKER_END)}", canonical_text, re.DOTALL)
    if not m:
        sys.exit(f"ERROR: {MARKER_BEGIN} / {MARKER_END} markers not found in the canonical spec text")
    block_lines = m.group(1).splitlines()

    managed = {"This version", "Latest version", "Previous version"}
    passthrough = []
    for line in block_lines:
        bm = BULLET_RE.match(line)
        if bm and bm.group(1) in managed:
            continue  # canonical only ever defines "This version"; drop it, we rebuild it below
        passthrough.append(line)

    new_lines = [
        f"- **This version:** `{this_version_url}`",
        f"- **Latest version:** `{latest_url}`",
    ]
    if previous_url:
        new_lines.append(f"- **Previous version:** `{previous_url}`")
    new_lines.extend(passthrough)

    new_block = MARKER_BEGIN + "\n" + "\n".join(new_lines) + "\n" + MARKER_END
    start, end = m.span()
    return canonical_text[:start] + new_block + canonical_text[end:]


def banner(source: str) -> str:
    return (
        "<!--\n"
        "  GENERATED FILE — do not edit directly.\n"
        f"  Source: {source}\n"
        "  Regenerate: blygger-org/sync_spec.py (see docs/spec-publishing-plan.md)\n"
        "-->\n\n"
    )


def footer(sha: str) -> str:
    return f"\n\n---\n\n*Published from [{GITHUB_REPO}@{sha}]({GITHUB_URL}/commit/{sha}).*\n"


def superseded_notice(successor: str) -> str:
    """Forward-linking banner for a superseded version's latest page (decision #23).

    Latest pages only — dated snapshots are immutable and never carry it."""
    url = f"{SITE_ORIGIN}/spec/{successor}/"
    return (
        f"> **Superseded by [version {successor}]({url}).** This document is no longer the "
        f"living specification and receives no further revisions — the status line below is "
        f"its final state. It stays permanently citable, and its dated snapshots are "
        f"unchanged. Implementors should read [version {successor}]({url}), which is a "
        f"standalone-complete superset of this text."
    )


def insert_after_title(text: str, block: str) -> str:
    """Place a block directly under the document's H1, above its status header."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("# "):
            return "\n".join(lines[: i + 1] + ["", block] + lines[i + 1 :])
    return block + "\n\n" + text


def render_spec_page(
    version: str,
    this_version_url: str,
    latest_url: str,
    previous_url: str | None,
    superseded_by: str | None = None,
) -> str:
    canonical_path = CANONICAL_FILES[version]
    if not canonical_path.is_file():
        sys.exit(f"ERROR: canonical spec not found at {canonical_path} (is blygger-spec checked out as a sibling of this repo?)")

    if spec_repo_is_dirty():
        print(f"WARNING: {SPEC_REPO} has uncommitted changes — publishing from a dirty tree.", file=sys.stderr)

    text = canonical_path.read_text("utf-8")
    text = rewrite_links_block(text, this_version_url, latest_url, previous_url)
    if superseded_by:
        text = insert_after_title(text, superseded_notice(superseded_by))
    sha = spec_repo_sha()
    return banner(f"blygger-spec/docs/{canonical_path.name}") + text.rstrip("\n") + footer(sha)


def sync_latest(version: str) -> None:
    latest_url = f"{SITE_ORIGIN}/spec/{version}/"
    snapshots = existing_snapshots(version)
    previous_url = f"{SITE_ORIGIN}/spec/{version}/{snapshots[-1]}/" if snapshots else None

    _, superseded_by = status_of(version)

    out_dir = CONTENT_SPEC / version
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "index.md"
    out_path.write_text(
        render_spec_page(version, latest_url, latest_url, previous_url, superseded_by), "utf-8"
    )
    print(f"  wrote {out_path.relative_to(ROOT)}" + (f" (superseded by {superseded_by})" if superseded_by else ""))


def cut_snapshot(version: str) -> None:
    _, superseded_by = status_of(version)
    if superseded_by:
        sys.exit(
            f"ERROR: {version} is superseded by {superseded_by} and receives no further "
            f"revisions (decision #23) — there is nothing new to snapshot. Its existing "
            f"snapshots stay citable; snapshot {superseded_by} instead."
        )
    if spec_repo_is_dirty():
        sys.exit(f"ERROR: {SPEC_REPO} has uncommitted changes — a snapshot must correspond to a pushed commit. Commit/push first.")
    if not spec_repo_head_is_pushed():
        sys.exit(f"ERROR: {SPEC_REPO}'s HEAD isn't pushed (or has no upstream) — a snapshot must correspond to a pushed commit. Push first.")

    date = datetime.now(timezone.utc).date().isoformat()
    snapshot_dir = CONTENT_SPEC / version / date
    if snapshot_dir.exists():
        sys.exit(f"ERROR: {snapshot_dir.relative_to(ROOT)} already exists — snapshots are immutable, refusing to overwrite.")

    snapshots = existing_snapshots(version)
    previous_url = f"{SITE_ORIGIN}/spec/{version}/{snapshots[-1]}/" if snapshots else None
    this_version_url = f"{SITE_ORIGIN}/spec/{version}/{date}/"
    latest_url = f"{SITE_ORIGIN}/spec/{version}/"

    sha = spec_repo_sha()
    tag = f"spec/{version}/{date}"
    existing_tag_sha = None
    try:
        existing_tag_sha = run("git", "rev-list", "-n", "1", tag, cwd=SPEC_REPO)
    except subprocess.CalledProcessError:
        pass
    head_full_sha = run("git", "rev-parse", "HEAD", cwd=SPEC_REPO)

    if existing_tag_sha and existing_tag_sha != head_full_sha:
        sys.exit(f"ERROR: tag {tag} already exists on a different commit ({existing_tag_sha[:7]} != {head_full_sha[:7]}).")
    elif existing_tag_sha:
        print(f"  tag {tag} already exists at HEAD — no-op.")
    else:
        run("git", "tag", tag, cwd=SPEC_REPO)
        run("git", "push", "origin", tag, cwd=SPEC_REPO)
        print(f"  created + pushed tag {tag}")

    snapshot_dir.mkdir(parents=True, exist_ok=True)
    (snapshot_dir / "index.md").write_text(render_spec_page(version, this_version_url, latest_url, previous_url), "utf-8")
    print(f"  wrote {(snapshot_dir / 'index.md').relative_to(ROOT)}")

    sync_latest(version)  # latest's Previous-version link now points at this snapshot


def build_spec_index() -> None:
    lines = [
        banner("derived from content/spec/ + blygger-spec tags").rstrip("\n"),
        "",
        "# Blygger Protocol — Specification Index",
        "",
        f"Source: [{GITHUB_REPO}]({GITHUB_URL})",
        "",
        "Each protocol version has its own standalone-complete document. The "
        "highest-numbered version is the living one, where revisions land; earlier "
        "versions are superseded — frozen, still citable, with their dated snapshots "
        "intact.",
        "",        "**Which version to implement:** the living one, from this site. **Pin to a "
        "dated snapshot** when you need the text to hold still — each snapshot below "
        "links a diff to the one before it. The `docs/` copy on the repository's `main` "
        "branch is the same text and may run a few days ahead of this page. **The plan "
        "documents and the reference client's source are not the specification**: "
        "constructs that have been decided but not yet built are listed in the living "
        "document's final section, labelled not yet normative, before any client emits "
        "them. Pre-1.0, every version is a draft and makes no wire promise; a superseded "
        "version stays conformant and merely lacks the newer constructs, because levels "
        "are strict supersets.",
        "",
        "| Version | Status | Latest revision |",
        "|---|---|---|",
    ]
    for version in sorted_versions():
        status, successor = status_of(version)
        cell = f"{status} — see [{successor}](/spec/{successor}/)" if successor else status
        lines.append(f"| {version} | {cell} | [/spec/{version}/](/spec/{version}/) |")

    for version in sorted_versions():
        snapshots = existing_snapshots(version)  # ascending
        if not snapshots:
            continue
        lines.append("")
        lines.append(f"## {version} snapshots")
        lines.append("")
        for i, date in enumerate(reversed(snapshots)):  # newest first for display
            url = f"/spec/{version}/{date}/"
            row = f"- [{date}]({url})"
            older_idx = len(snapshots) - 1 - i - 1
            if older_idx >= 0:
                older = snapshots[older_idx]
                compare = f"{GITHUB_URL}/compare/spec/{version}/{older}...spec/{version}/{date}"
                row += f" — [diff since {older}]({compare})"
            lines.append(row)

    lines.append("")
    lines.append("## Reference implementation")
    lines.append("")
    # The client has its own repo since 2026-09-28 (blygger-spec session 26) and
    # its own tagged releases since 0.4.1; the `ref-v*` tags this used to look
    # for in blygger-spec were never cut. Client versions are not protocol
    # versions — the client's CHANGELOG names the protocol version it implements.
    lines.append(
        f"[blygger/blygger-studio]({STUDIO_URL}) — tagged releases at "
        f"[{STUDIO_REPO}/releases]({STUDIO_URL}/releases). The client's version is not "
        "the protocol's; each release names the protocol version it implements. The "
        "client's source is not the specification."
    )

    CONTENT_SPEC.mkdir(parents=True, exist_ok=True)
    out_path = CONTENT_SPEC / "index.md"
    out_path.write_text("\n".join(lines) + "\n", "utf-8")
    print(f"  wrote {out_path.relative_to(ROOT)}")


def discover_notes() -> list[dict]:
    """Parse every docs/notes/tn-*.md into a header record — the sync script
    reads title/date/status off the note's own first lines (README.md's
    documented convention), no separate front matter needed."""
    if not NOTES_DIR.is_dir():
        return []
    notes = []
    for path in sorted(NOTES_DIR.glob("tn-*.md")):
        m = NOTE_FILENAME_RE.match(path.name)
        if not m:
            continue
        number, slug = int(m.group(1)), m.group(2)
        text = path.read_text("utf-8")
        lines = text.splitlines()
        title_m = NOTE_TITLE_RE.match(lines[0]) if lines else None
        title = title_m.group(1).strip() if title_m else slug.replace("-", " ")
        head = text[:1000]
        date_m = DATE_RE.search(head)
        date = date_m.group(0) if date_m else ""
        sup_m = SUPERSEDED_RE.search(head)
        status = f"superseded by {sup_m.group(1)}" if sup_m else "current"
        notes.append({
            "number": number, "slug": slug, "path": path,
            "title": title, "date": date, "status": status, "text": text,
        })
    return notes


def render_note_page(note: dict, sha: str) -> str:
    return banner(f"blygger-spec/docs/notes/{note['path'].name}") + note["text"].rstrip("\n") + footer(sha)


def build_notes_index(notes: list[dict]) -> None:
    lines = [
        banner("derived from content/notes/").rstrip("\n"),
        "",
        "# Blygger Technical Notes",
        "",
        "Numbered, non-normative documents recording design reasoning alongside "
        "the spec — especially rejected designs and the rationale that closed "
        "them. Notes constrain nothing; the spec is the only normative text.",
        "",
        "| Note | Date | Status |",
        "|---|---|---|",
    ]
    for note in sorted(notes, key=lambda n: n["number"]):
        url = f"/notes/tn-{note['number']}/"
        lines.append(f"| [TN-{note['number']} — {note['title']}]({url}) | {note['date']} | {note['status']} |")

    CONTENT_NOTES.mkdir(parents=True, exist_ok=True)
    out_path = CONTENT_NOTES / "index.md"
    out_path.write_text("\n".join(lines) + "\n", "utf-8")
    print(f"  wrote {out_path.relative_to(ROOT)}")


def sync_notes() -> None:
    notes = discover_notes()
    if not notes:
        return
    sha = spec_repo_sha()
    for note in notes:
        out_dir = CONTENT_NOTES / f"tn-{note['number']}"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "index.md"
        out_path.write_text(render_note_page(note, sha), "utf-8")
        print(f"  wrote {out_path.relative_to(ROOT)}")
    build_notes_index(notes)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", nargs="?", default="latest", choices=["latest", "snapshot"])
    parser.add_argument(
        "--version",
        default=living_version(),
        choices=list(SPEC_VERSIONS),
        help="snapshot mode only; defaults to the living version. Latest mode always syncs every version.",
    )
    args = parser.parse_args()

    if not SPEC_REPO.is_dir():
        sys.exit(f"ERROR: {SPEC_REPO.resolve()} not found — blygger-spec must be checked out as a sibling of blygger-org.")

    if args.mode == "snapshot":
        cut_snapshot(args.version)
    else:
        # Every version, not just the living one: a supersession flips an older
        # version's page (it gains the forward-linking banner), so regenerating
        # only the newest would leave that page stale.
        for version in sorted_versions():
            sync_latest(version)

    build_spec_index()
    sync_notes()


if __name__ == "__main__":
    main()
