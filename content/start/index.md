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

**Fifteen minutes, one command.** You need a Cloudflare account and a domain
already on it.

```
git clone https://github.com/blygger/blygger-studio my-blyg
cd my-blyg
npm install --legacy-peer-deps
npm run init
```

`init` asks which Cloudflare account to use — explicitly, even if you only have
one, because a deploy to the wrong account succeeds silently — then provisions
your database and media bucket, writes your config, applies the schema, and
prompts for your password. It never sees that password: wrangler does the
prompting. Your session signing key is generated for you rather than invented by
you, which is the right way round.

Then:

```
npm run deploy
```

and your blyg is at `https://blyg.yourdomain.com/`, with the studio at
`/studio`. Re-run `init` any time — it checks before it creates, so a second run
after a failure picks up where it stopped rather than building a second
database.

**Staying current matters more than starting.** `npm run upgrade` fetches the
new release, shows you what changed and whether any of it touches your database,
merges while keeping your config, applies migrations, and runs the test suite
*before* it offers to deploy. Pre-1.0 the wire format itself can change between
releases, so this is not optional maintenance — it is how you stay legible to
the blygs reading you. Every changelog entry states `Migrations:` on its own
line, which is the one line to read before upgrading.

**When it looks the way you want, consider listing it at
[blygger.com](https://blygger.com).** Suggested, not required, and worth being
clear about why it is only a suggestion: nothing in the protocol needs a
registry, and an unlisted blyg works exactly as well as a listed one — people
reach it by its URL, its feed, and the blogrolls of people who read it.
The directory is how *strangers* find you, and nothing else. It also runs the
real resolution algorithm against your URL when you submit, so it doubles as a
free conformance check on a blyg you have just stood up.

**A path mount** (`yourdomain.com/blyg/`) is fully supported by the protocol and
people run them — but `init` will not generate one, because `/studio` and `/api`
are host-rooted whatever mount you choose, so a path mount on a domain already
serving `/api` collides with it. Use a subdomain unless you know that path space
is free; if you want a path, the config shape is in
[`wrangler.jsonc`](https://github.com/blygger/blygger-studio/blob/main/wrangler.jsonc).

**Leaving is a command, not a negotiation.** `npm run export` writes your entire
blyg as static files. That is the answer to "what if Cloudflare goes away", and
it works on day one rather than being promised for later.

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

### Which text to build against

This is the question most likely to waste your afternoon, so it gets its own
section. There are four things on this site that look like a specification, and
only two of them are one.

**1. The living spec — [blygger.org/spec/](/spec/).** The highest-numbered
version. This is what to implement against. It is standalone and complete: a
`/spec/{version}/` URL hands you one whole document, and you never chase deltas
through a changelog. Revisions land here, so it can move under you — usually in
the direction of saying more clearly what it already meant.

**2. A dated snapshot — `/spec/{version}/{date}/`.** Immutable, forever. **Pin
here when you need the text to hold still**: while you are building, while you
are testing conformance, or any time you want to be able to say *which* text you
implemented. Each snapshot links a diff to the one before it, so catching up is
a diff rather than a re-read. If you are shipping something other people depend
on, pin.

**3. The living document's final section — not normative, and this is the trap.**
Every living spec ends with a section carrying constructs that have been
*decided* but not yet *built*. They are there on purpose and clearly labelled: we
write the ruling down before anyone implements it, so the reasoning is public
while it can still be argued with. But a construct sitting there has not been
exercised across two implementations yet, and its shape can still move.
**Do not build from that section unless you mean to** — see below, because
sometimes you should.

**4. The plan documents and the reference client's source — not the spec at
all.** `v0.4-plan.md` is a work plan. `blygger-studio` is one implementation of
the spec and is wrong about it from time to time; when the two disagree, the
spec wins and the client has a bug. Neither is a normative source and neither
carries any promise.

**Superseded versions are still conformant.** Levels are strict supersets and
unknown constructs are ignored rather than rejected, so a client implementing an
older version is not broken — it simply lacks the newer constructs. There is no
deadline and nothing stops working.

### If you *want* to build against unfrozen text

Please do, and say so. Implementing a decided-but-unbuilt construct before it
freezes is the most useful thing anyone outside this project can do: it is how a
shape gets found to be wrong while changing it is still cheap. Two rules make it
work rather than hurt:

- **Pin the snapshot you built against and say which one**, in your README or
  your manifest's `generator_url` target. "It broke" is hard to act on;
  "it broke against the 2026-09-28 snapshot" is a bug report.
- **File what you find**, at
  [blygger-spec/issues](https://github.com/blygger/blygger-spec/issues). The
  template asks which spec version and which implementation, because there are
  now several of both. A construct that survives a second implementation is
  ready to freeze; one that does not, needed you.

**Pre-1.0, no version makes a wire promise** — including the living one. That is
stated here rather than buried in a status page, because it is the thing you are
actually deciding about.
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
