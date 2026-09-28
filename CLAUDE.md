# blygger-org

> **Environment rules, keys & safety policies:** see [Code/CLAUDE.md](../../CLAUDE.md) — read before starting work.
> **Protocol spec + reference implementation:** [`../blygger-spec/`](../blygger-spec/) — read `blygger-spec/CLAUDE.md` and `blygger-spec/docs/` before touching anything that isn't purely presentational; this repo is a *client* of the protocol, not where protocol decisions get made.

The public face of the Blygger protocol at **blygger.org**: commons/spec-adjacent —
the namespace-URI domain and the published home of the normative spec (`/spec/`),
technical notes (`/notes/`) and the namespace page (`/ns/0.1`).

**It does not run a blyg, and is not a test node.** The session-6 scaffold said it
would be one of the two initial cross-client test instances; session 11 put those on
`venkateshrao.com/blyg/` and `blyg.protocol-institute.org` instead, and this site's
job settled into being the stable citable home of the normative text. The relevant
plan doc is [`blygger-spec/docs/spec-publishing-plan.md`](../blygger-spec/docs/spec-publishing-plan.md)
(executed sessions 11–12, 20), not `deploy-stub-sites-plan.md`.

## Talks

A third published genre alongside normative spec text and technical notes, added
session 21 (2026-09-16). One editable source file per talk:

| Path | Role |
|---|---|
| `talks/<slug>/talk.md` | **The whole deck.** YAML frontmatter + every slide. |
| `talks/<slug>/images/` | Copied to `dist/talks/<slug>/images/`. |
| `talks/<slug>/brief.md` | Operator input. Deliberately **not** published. |

`talk.md` format: `# Heading` starts a section, `## Heading` starts a slide, a
markdown `![alt](path)` is the slide's image, the list is what gets projected, and
`**Cues**` / `**Notes**` blocks are the speaker's prompts and the why-this-slide note.
Slides are numbered **by position**, so inserting or reordering renumbers the rest —
there are no ids to keep in sync.

This started as a `slides.yaml` + `track.md` pair and was collapsed after one round:
splitting "what is projected" from "what is said" meant every content edit touched two
files and kept them aligned by hand, which is how a renumber once produced two slides
sharing an id. Positional numbering makes that class of bug unrepresentable rather than
guarded against.

Bullets are rendered through the markdown pipeline, which is what buys sub-bullets and
inline `code`/**emphasis** on the stage. `normalize_list_indent()` re-indents nested
items to the 4 spaces Python-Markdown's `sane_lists` requires, so 2-space nesting — the
thing anyone actually types — works instead of silently flattening.

`build_talk.py` renders this into a deck (16:9 stage, prev/next, fullscreen, deep links
to `#slide-NN`) plus a readable transcript. Ported from
`protocol-institute/humboldt/humboldt-site/build.py::_build_talk`, minus the audio
machinery — humboldt gates its whole player on audio existing, which had to be inverted
here since an operator drives the deck.

**Everything inside the stage is sized in `cqh`** (the stage is a `container-type: size`
container), so the embedded preview and the fullscreen presentation are one composition
at two scales. Anything added to the stage should be in `cqh` too — sizing in `rem`/`vw`
is what left a 2-pixel screenshot on one slide while fullscreen looked fine.

A slide with no bullets is treated as a placeholder and marked on the page; missing
images warn at build time.

## Presentation style — owned by `talk-kit`

The deck's **visual theme and content limits are shared** with the other symposium
talks and are **not maintained here**. They live in
[`Code/talk-kit/`](../talk-kit/) (`../../talk-kit/` from here):

| File in this project | Canonical source |
|---|---|
| `talk-theme.css` | `talk-kit/theme/talk-theme.css` |
| `talk-content-guide.md` | `talk-kit/theme/talk-content-guide.md` |

**Both are synced copies. Do not edit them here.** `talk-kit/sync.py` is their only
writer and will overwrite local edits without warning; each file carries a banner
saying so. A style change belongs in talk-kit, then `./sync.py`, then rebuild here.

What *does* belong here is **content**: slides, bullets, cues, diagrams. The split is
the point — style is shared across three decks, slides are this talk's alone.

`talk-content-guide.md` is the one to read before writing slides. It is measured, not
opinion: **14 lines of bullet text** with a one-line title, 11 if every bullet is
short, **6 with a diagram**, ~37 characters of title, 9 table rows. Over-budget
content is **clipped silently** — no scrollbar, no warning, and a clipped list looks
exactly like a short list. `talk-kit/reference/check-deck.js`, pasted into the console
on a built deck, is the only thing that catches it.

## Stack

Static site: Python (`build.py` + `markdown` package) renders `content/*.md`
through `templates/page.html` into `dist/`, styled by `site.css`. Deployed to
Cloudflare Pages (project `blygger-org`) via `deploy.sh`. The reference client is
a separate repo — [`blygger/blygger-studio`](https://github.com/blygger/blygger-studio),
checked out at `../blygger-studio/`, split out of `blygger-spec/worker/` and renamed
from `blyg-ref` at session 26 (2026-09-28). Nothing client-side is built here.

**This repo is Track 4** of the program roadmap
([`blygger-spec/docs/roadmap-tracks.md`](../blygger-spec/docs/roadmap-tracks.md)):
developer-community management — the published spec, getting started, and the
ecosystem directory of community-built clients, tools, integrations and mods.

## Structure

- `content/` — publishable site content (session 7): `overview.md` (landing-page
  protocol overview, canonical here); `spec/` (session 11, 2026-08-09 —
  **entirely generated**, see below). Publish mapping + source-of-truth rule:
  `content/README.md`.
- `templates/page.html`, `site.css` — shared page shell + stylesheet. Signature
  design element: a monospace "log rail" in the left margin turning each page's
  headings into a numbered index (real section numbers on the spec page,
  positional on the overview page) — echoes the protocol's own
  "your feed is the changelog" idea.
- `sync_spec.py` (session 11) — the only writer of `content/spec/`. Publishes
  the canonical spec from the sibling `../blygger-spec/docs/protocol-v0.1.md`
  checkout; also (re)generates `content/spec/index.md`, the version/snapshot
  table. Design doc: `blygger-spec/docs/spec-publishing-plan.md`.
- `build.py` — renders `content/` → `dist/` (gitignored); walks `content/spec/`
  recursively so it picks up the index page, each version's latest revision,
  and any dated snapshots without needing per-page edits. `deploy.sh`
  (gitignored; reads `CLOUDFLARE_API_TOKEN`/`CLOUDFLARE_ACCOUNT_ID` from
  `Code/.env.keys`, never hardcodes them) — runs `sync_spec.py` then
  `build.py` then `wrangler pages deploy`.

### Publishing a spec update

Day-to-day: edit `../blygger-spec/docs/protocol-v0.1.md`, commit + push there,
then from this repo run `./deploy.sh` (syncs latest, builds, deploys) — no
manual copying, ever.

Cutting a citable dated snapshot (a deliberate editorial act, not routine —
see `spec-publishing-plan.md` §2 "Snapshot policy"): from this repo,
`/opt/homebrew/bin/python3 sync_spec.py snapshot`. Requires a **clean,
pushed** `../blygger-spec` tree (refuses otherwise — a snapshot must
correspond to a real, citable commit). This creates + pushes a
`spec/0.1/YYYY-MM-DD` tag in `blygger-spec`, writes the immutable dated page,
regenerates latest's "Previous version" link, and regenerates the index —
then run `./deploy.sh --no-build` (or plain `./deploy.sh`) to publish it.

## Workflow Notes

- Git repo: `blygger/blygger-org` (public), branch `main`.
- Deployed to: Cloudflare Pages, live at both
  [blygger.org](https://blygger.org) and
  [blygger-org.pages.dev](https://blygger-org.pages.dev) — the custom domain's
  DNS record was added by hand and activated 2026-08-04 (see `status.md`).

## Status

See [`status.md`](status.md).
