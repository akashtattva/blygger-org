# Build a blyg

Three ways in, ordered by how much work they are. The first one is free and you
may have done it already.

## 1. You might already be halfway in

If your site has an **RSS or Atom feed**, blygs can subscribe to you today. No
software to install, no change to your site, no cooperation required at your
end — a blyg reader resolves your feed and imports your items the same way it
imports another blyg's.

What you don't get, without going further, is being *quotable*: transclusion —
someone baking a snapshot of your writing into their piece, with provenance
recording exactly which version they quoted — needs your side to publish the
item documents that make a snapshot possible.

So: readable is free. Quotable is the upgrade.

**Try it:** [submit your feed to the directory](https://blygger.com) and see
what a blyg client makes of it. Submission runs the real resolution algorithm
and tells you what it found.

## 2. Host a blyg on Cloudflare

**[Blygger Studio](https://github.com/blygger/blygger-studio)** is a small
Cloudflare Worker — publishing, subscribing, blogrolls, curated lists, and
instructed generation, with the published output as pure static files. It is the
reference client, and it is one client among several (see §3).

It lives in its own repository as of 2026-09-28, and was called `blyg-ref` before
that. If you are running a node that reports `blyg-ref/0.3.0`, it is the same
software under an older name and nothing about your deployment has changed.

**Status: planned, not shipped.** A template repository plus an interactive
`npm run init` that provisions the database and storage, writes your config,
applies migrations, and prompts for your secrets. Design is written up in
[`self-host-plan.md`](https://github.com/blygger/blygger-spec/blob/main/docs/self-host-plan.md);
the tooling is not built yet.

Standing one up by hand is possible today — the client is
[MIT-licensed](https://github.com/blygger/blygger-studio), and **five live nodes
run it, three of them stood up by people we have never spoken to**, working from
this page alone. So the dozen-odd manual steps are evidently survivable; they are
still a dozen steps with two copy-the-generated-id-back-into-config loops, which
is what the tooling exists to remove. If you want to do it by hand, the
deployment shape is in
[`wrangler.jsonc`](https://github.com/blygger/blygger-studio/blob/main/wrangler.jsonc).

Something wrong with the client? [File it against
Blygger Studio](https://github.com/blygger/blygger-studio/issues/new/choose) — not
against the spec, unless another client would have to change too.

## 3. Build a client

**People are doing this, and it turns out to be the most interesting thing
happening here.** As of 2026-09-28 there are **seven** client implementations
publishing live blygs, and six of them are not ours:
`Blynger`, `sachin-blyg`, `caseyjr-blyg`, `blyg-publisher` (an Obsidian plugin),
`goddinpotty-blyg` (a Roam-to-static publisher taught to emit a blyg), and one
hand-rolled client at `thinking.drwip.com` that predates our talk. Alongside them
are tools that author *into* an existing blyg rather than producing one — a native
macOS studio, a Drafts action.

If you build one, **[tell us](https://github.com/blygger/blygger-org/issues/new/choose)**
and it gets listed. Nobody has forked our repos — people read the spec and write
their own — which means we cannot see your work unless you say so.

- **[The spec](/spec/0.2/)** — standalone and complete. A `/spec/{version}/` URL
  hands you one whole document; you never chase deltas through a changelog.
- **[Technical notes](/notes/)** — non-normative records of *why*, especially of
  designs that were rejected.
- **[The CSS contract](https://github.com/blygger/blygger-spec/blob/main/docs/css-contract.md)**
  — which classes are visible on the wire and what any client owes them.
- **Conformance levels L0–L3** are strict supersets, and unknown constructs are
  ignored rather than rejected, so a partial implementation is a *conformant*
  implementation.

**The open gap, and the 1.0 gate.** This section used to say there was exactly
one implementation, and that one implementation is not a protocol but a program
with a spec next to it. That stopped being true in September 2026, and the gate it
guarded has largely been met from the outside rather than by us.

What is still genuinely missing is a client on a deliberately different
substrate: **local-first — a folder on a laptop, authoring on-device, deploying to
a dumb static host**, with no server in the publishing path at all. The Obsidian
and Hugo integrations are the closest anyone has come. That shape is the real test
of the static-files-and-RSS claim, because it is the one where nothing dynamic
exists to paper over a gap in the spec.

A second thing now wanted, which the first version of this page could not have
anticipated: **a conformance checker anyone can run.** With seven implementations
and live nodes split across protocol 0.2 and 0.3, "conformant" can no longer mean
"passes our tests".

## What you're signing up for

**No version before 1.0 is stable, including the wire format.** Building clients
is how this protocol gets tested, so the spec changes when building finds
something — twice in the last month it did, and now six other implementations are
finding things too.

That is a real cost and it is stated here rather than buried: read it,
implement it, argue with it, but don't build something load-bearing on it yet
and expect the ground to hold still.

What *is* stable, because it costs nothing to promise: every blyg feed is valid
RSS, the published surface is static files, and nothing about the protocol
requires a company in the middle.
