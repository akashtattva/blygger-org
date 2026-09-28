# content/ — publishable pages for blygger.org

Source content for the blygger.org site, written session 7 (2026-08-03).
`build.py` renders every `.md` here into `dist/`.

## Publish mapping

| File | URL | Role |
|---|---|---|
| `overview.md` | `blygger.org/` | Human-readable high-level protocol overview — the landing-page content |
| `ns/0.1/index.md` | `blygger.org/ns/0.1` | Descriptive note on the `blyg:` XML namespace, for implementors who dereference the namespace URI found in a feed. Written session 15 (2026-09-11); its "Versioning of this namespace" section is the public face of locked decision #22 (namespace URI is permanent, never tracks the protocol version). |
| `spec/index.md` | `blygger.org/spec/` | Generated index of all spec versions + dated snapshots |
| `spec/{version}/index.md` | `blygger.org/spec/{version}/` | Generated: latest revision of that protocol version |
| `spec/{version}/{date}/index.md` | `blygger.org/spec/{version}/{date}/` | Generated: immutable dated snapshot |
| `notes/index.md` | `blygger.org/notes/` | Generated index of all technical notes |
| `ecosystem/index.md` | `blygger.org/ecosystem/` | Generated directory of community-built clients, tools, integrations and mods (session 26). Written by `sync_ecosystem.py` from `ecosystem/projects.toml` plus a live census of every blyg listed at blygger.com |
| `notes/tn-{N}/index.md` | `blygger.org/notes/tn-{N}/` | Generated: technical note N, latest text from `main` (no dated snapshots — see `spec-publishing-plan.md` §5) |

## Source-of-truth rule

**Everything under `spec/` and `notes/` is generated — `sync_spec.py` is the
only writer. Hand-editing is prohibited** (session 11, 2026-08-09 for
`spec/`; retires the earlier hand-copy convention; extended to `notes/`
session 16). The canonical spec lives in
`../blygger-spec/docs/protocol-v0.1.md`, canonical notes in
`../blygger-spec/docs/notes/tn-*.md` — all edits happen there; run
`/opt/homebrew/bin/python3 sync_spec.py` (latest mode, default) or
`sync_spec.py snapshot` to republish. Every run of `sync_spec.py` refreshes
both `spec/` and `notes/` — there is no separate notes CLI mode; notes have
no dated-snapshot tier (design rationale: `spec-publishing-plan.md` §5).
Every generated file carries a `GENERATED FILE — do not edit directly`
banner comment and a footer provenance stamp naming the source commit. See
`blygger-spec/docs/spec-publishing-plan.md` for the full design and
`../CLAUDE.md` for the day-to-day how-to.

**`ecosystem/` is generated too, by a different writer.** `sync_ecosystem.py` is the
only writer of `content/ecosystem/`; its curated input is `../ecosystem/projects.toml`,
which **is** hand-edited and is the authoritative answer to *what gets listed*. The
script enriches and checks entries and reports repos it discovered that are not listed,
but it never adds one — listing is an editorial act, as it is at blygger.com. Run
`/opt/homebrew/bin/python3 sync_ecosystem.py` to refresh; `--offline` rebuilds from cache
with no network, and `--summaries` regenerates README-derived summaries (needs
`AI_PROVIDER_KEY`; without it, entries fall back to their own or GitHub's description).

`overview.md` is canonical *here* — it is site copy, not protocol doctrine; the
spec and `blygger-spec` docs win on any conflict. The same applies to
`ns/0.1/index.md`: it restates wire constructs the spec defines normatively
(feed elements, the GUID scheme) and says so on its face, so it must be
re-checked against `protocol-v0.1.md` §7 whenever those change. It is
hand-written, not generated — `sync_spec.py` does not touch anything outside
`spec/`.
