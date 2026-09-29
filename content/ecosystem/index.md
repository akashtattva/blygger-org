<!-- GENERATED FILE — do not edit directly. Written by sync_ecosystem.py. -->
<!-- Curated source: ecosystem/projects.toml. Run ./sync_ecosystem.py to refresh. -->

# The Blygger ecosystem

Everything we know of that speaks Blygger, whoever built it. **Listing is not endorsement and not a conformance claim** — several of these we have only read the manifest of, and one describes itself as "vibecoded, no warranty".

Built something? **[Submit it](https://github.com/blygger/blygger-org/issues/new/choose)** — or tell us about someone else's, and we will check with them.

## Where things stand

- **9 client implementations** publishing **11 live blygs** — 6 of those clients are not ours.
- Protocol versions in the wild: **0.3** (8 nodes), **0.2** (3 nodes).
- **11 projects listed** below.

The client counts come from reading every manifest in [blygger.com's directory](https://blygger.com), which is how a client becomes visible at all: `generator` is a public key in a file the protocol requires, so publishing announces you whether or not your source is anywhere we can see. Five of the clients below have no locatable repository.

**Tools and mods do not work that way.** They carry no `generator`, and nobody has forked our repositories — people read the spec and write their own — so there is no fork graph to walk. If you built one and did not tell us, it is not on this page.

## Clients

Publish a blyg of their own, and so carry their own `generator` string. A client is discoverable the moment it publishes — this is the one category we can census without being told.

### [Blygger Studio](https://github.com/blygger/blygger-studio) — ours

The reference client. A Cloudflare Worker that publishes a blyg, subscribes to others, and threads, transcludes and responds across them. Named blyg-ref until 2026-09-28.

`blygger-studio/0.7.0` · TypeScript · updated today

**3 of 5 live nodes run an older build** `blyg-ref/0.3.0`, `blygger-studio/0.7.0` rather than `blygger-studio/0.8.0`.

Live: [And Yet Here We Are](https://blyg.aneeshsathe.com/) (protocol 0.3), [Kyle's blyg](https://blyg.bricolage.io/) (protocol 0.3), [Protocol Institute Blyg](https://blyg.protocol-institute.org/) (protocol 0.3), [\[jdbb\] studio blyg](https://jd-blyg.exe.xyz/) (protocol 0.3), and 1 more

### [Blynger](https://bradydale.com/blyg/)

An independent client on its own version line, already at 0.8.2. Publishes protocol 0.3. Source not located — if this is yours, tell us where it lives.

`Blynger/0.8.2`

Live: [bradydale.com/blyg](https://bradydale.com/blyg/)

### [caseyjr-blyg](https://caseyjr.org/blyg/)

An independent client publishing protocol 0.2. Source not located.

`caseyjr-blyg/0.1.0`

Live: [Mike Casey](https://caseyjr.org/blyg/) (protocol 0.3)

### [sachin-blyg](https://blyg.sachinbenny.xyz/)

An independent client publishing protocol 0.3. Source not located.

`sachin-blyg/0.1.0`

Live: [blyg.sachinbenny.xyz](https://blyg.sachinbenny.xyz/)

### [thinking.drwip.com's client](https://thinking.drwip.com/blyg/)

The first independent implementation, and the first blyg on a path mount rather than a subdomain — its manifest predates the September 2026 talk. Publishes protocol 0.2. Source not located.

`thinking.drwip.com`

Live: [Dr Wip · Landscape of Thought](https://thinking.drwip.com/blyg/) (protocol 0.2)


## Integrations

Teach an existing publishing system — Hugo, Obsidian, a note-taking tool — to emit a conformant blyg.

### [blyg-publisher](https://github.com/brndnpink/blyg-publisher)

Obsidian plugin that publishes a Blygger blyg from one folder of your vault to a static host. Local-first. Includes an AI-agent setup runbook (AGENTS.md).

`blyg-publisher/0.0.1` · TypeScript · MIT · updated yesterday

Live: [Lightsong](https://lightsong.ink/blyg/) (protocol 0.2)

### [hugo-blyg](https://github.com/chrisbodhi/hugo-blyg)

build a Blygger feed with Hugo & publish with GH Actions

Python · updated today

### [goddinpotty-blyg](https://github.com/mtravers/goddinpotty)

A Roam-to-static publisher taught to emit a blyg. Publishes protocol 0.2. The repo link is goddinpotty itself; we have not located the blyg-emitting fork.

`goddinpotty-blyg/0.1`

Live: [AMMDI Blyg](https://ammdi.hyperphor.com/blyg/) (protocol 0.2)


## Authoring tools

Author *into* a blyg that already exists, rather than producing one. They carry no `generator`, so they are invisible to the census and are here because someone told us.

### [blygger-desktop](https://github.com/aneeshsathe/blygger-desktop)

A native, Notational-Velocity-fast macOS studio for Blygger blogs (blygs). Rust + GPUI. Vibecoded, no warranty.

Rust · MIT · updated today

### [drafts-blyg](https://github.com/miguelito4/drafts-blyg)

One-tap Blygger fragments from your phone via Drafts

JavaScript · MIT · updated yesterday


## Libraries and unclassified

Building blocks, and projects whose shape we have not yet confirmed with their author.

### [pioneering-spirit-blyg](https://github.com/patwater/pioneering-spirit-blyg)

Found by GitHub search; purpose not yet confirmed with its author, and no live blyg located. Listed so it is not lost.

Rust · updated today


## Publishing, but unidentified

These `generator` strings appear on live blygs and are not matched to any project above. If one is yours, [say so](https://github.com/blygger/blygger-org/issues/new/choose) and it gets a proper entry.

- `Blynger/0.8.3` — [bradydale.com/blyg](https://bradydale.com/blyg/)
- `sachin-blyg/0.2.0` — [blyg.sachinbenny.xyz](https://blyg.sachinbenny.xyz/)

<!-- Discovered on GitHub and NOT in ecosystem/projects.toml. Triage these,
     then add or deliberately skip each one:
       chrisbodhi/newschematic  (via code: blyg.json)
       msmsim/msn  (via code: blyg.json)
       mtravers/goddinpotty  (via code: blyg.json)
       protocolvision/sig-p4b  (via name/desc/readme)
-->

---

*Checked 2026-09-29. This page is regenerated, not hand-maintained: repository facts and live-blyg data are re-read on each run, so a stale entry here means the check has not run, not that nothing changed.*
