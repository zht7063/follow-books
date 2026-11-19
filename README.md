# follow-books — Dan Koe study edition

An **unofficial curated ebook reading prototype** for **Dan Koe only**: seven original editorial chapters, a source index, client-side search, source attribution and date provenance, previous/next reading navigation, and a responsive layout. It is independent, incomplete and unaffiliated. It does not republish Dan's books or full essays.

The 2026-11-19 seed contains 63 entries selected mainly for software, AI and digital products. This edition preserves that selection and its gaps. It is not a comprehensive writing archive or a five-person library. The older Chinese seed abstracts are clearly labelled; X remains URL-only and unread, and every video remains unwatched.

## Read locally

Python 3.13+ and Node 24+ are sufficient; **there are no third-party dependencies to install**.

```bash
npm run build
npm test
npm run check
python3 scripts/validate_content.py
python3 -m http.server 4173 --bind 127.0.0.1 --directory site
```

Open **http://127.0.0.1:4173/** on the machine running the server. A dedicated preview is left running for this implementation; its actual PID, port and address are in [docs/preview-server.json](docs/preview-server.json). Loopback is not a public URL and is not automatically reachable from another device.

GitHub Pages is not enabled. External preview requires a separately authorized hosting/forwarding step. This task does not configure Pages, domains or another hosting service.

## Collection, with a deliberate stop boundary

```bash
# Default: print the finite plan; no network, no metadata/cache writes.
python3 scripts/collect_thedankoe.py

# Explicit live collection, only where allowed; not needed to build or test.
python3 scripts/collect_thedankoe.py --live --budget 90 --delay 10

# Offline: update normalized metadata from existing local state and review notes.
python3 scripts/collect_thedankoe.py --export-only
```

This run **stopped after 17 requests** when a newsletter page returned a subscription/access marker. The stop is persistent and global. Re-running `--live` with that local state makes **zero additional requests**, even to another host. Do not delete the stop state to work around the restriction. The delivered site works from committed metadata and editorial without a live crawl.

The collector:

- Makes one request at a time, uses an honest research User-Agent with `zht7063@users.noreply.github.com`, and never creates a cookie jar or authenticates.
- Uses a fixed official-host allowlist and an explicit finite URL plan. The cap is 90 HTTP attempts per invocation, including robots, redirects and retries. The minimum configured delay is 8 seconds; this run used 10 seconds, increased if robots specifies a longer delay or request rate.
- Reads robots first, honors disallow/crawl-delay/request-rate, treats explicit machine-use restrictions conservatively, and fails closed when robots cannot be determined. A public robots 404/410 means no published rules; it is still recorded.
- Inspects redirects individually, checks robots at every destination, and never follows an unapproved host or a login/account redirect. Terms/access markers, restricted statuses (401/402/403/429/451), captcha/challenges and responses exceeding the 5 MiB inspection limit stop all collection. It never retries restrictions.
- Retries only transient network errors and 5xx, with at most three total attempts and 2/4-second backoff in addition to the request spacing. Reads known restricted statuses before bodies so a timeout cannot turn a 403 into a retry.
- Caches completed responses by normalized URL, strips URL fragments for deduplication, verifies local body hashes, and reuses completed entries across invocations. `--stale-after-days N` is an explicit opt-in refresh for an unblocked run; it never overrides a stop. No concurrency option exists.
- Does not fetch X, unofficial APIs, GitHub repositories, YouTube watch pages, videos or transcripts. Optional public channel/RSS metadata was planned but was not reached before the stop. The two conflicting seed channel IDs remain unresolved.

The request ledger records each actual HTTP attempt and its outcome. The summary distinguishes HTTP responses (including discovery and robots) from source entries; cache hits and skips are event counts, not unique-source counts. Unrequested sources retain platform/read labels and decision notes. No source date is inferred from fetch time or sitemap `lastmod`.

## Data and copyright boundaries

```text
original-info/                  immutable five-person seed snapshot
scripts/                        collector, static builder, publication guards
web/                            shared CSS and modest search JavaScript
editorial/thedankoe/             original commentary + hash-bound review notes
 data/thedankoe/sources.json     normalized metadata + short seed abstracts
 data/thedankoe/request-ledger.json  sanitized request decisions
 data/thedankoe/collection-summary.json  real counts and limits
 data/thedankoe/raw/             GITIGNORED HTML/XML bodies and private resume state
site/                           committed static output; safe to serve alone
tests/                          offline stdlib unittest + Node test fixtures
```

Raw bodies may be used for local analysis, but never enter the public tree or builder. The builder reads only normalized metadata, original editorial and shared UI assets. No AI-generated summary is attributed to Dan; organization-related material is labelled separately. Only the homepage and specified opening excerpts of two essays were newly reviewed; see [review notes](editorial/thedankoe/reviewed-sources.json). Fetched does not mean read.

The hygiene guard flags a contiguous overlap of 40 normalized tokens and at least 200 characters between a cached body and published/editorial text. Offline fixtures prove that long copies fail while short quotes pass. This heuristic catches obvious republication; it does not assess translated copying, close paraphrase or cumulative quotation. This edition uses original commentary and links, with no intentional article quotations beyond titles.

## Verification and evidence

`npm test` runs offline. Fixtures cover serial operation, cache/dedup/resume, robots and delays, restriction stops (including across process restarts), bounded retries, safe redirects, adapter read failures, metadata provenance, no-fulltext publication, chapter links, deterministic builds, search interactions and 375px CSS contracts. No browser GUI was driven; CSS/HTML/DOM contracts are evidence, not a screenshot or a complete accessibility audit.

[Implementation report](docs/thedankoe-prototype-report.md) records collection results, reviewed sources, validation, preview and PR details. GitHub Actions builds and checks the site entirely offline and has no deployment step.

`original-info/` remains a read-only archival snapshot. Its other four people are not included in this prototype, and no five-person routines were changed.
