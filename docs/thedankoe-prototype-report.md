# Dan Koe unofficial reader — implementation report

Recorded on 2026-11-19. This is a finite, independent reading prototype, not a complete archive or an authorized Dan Koe ebook.

## Delivery and provenance

- Repository: [zht7063/follow-books](https://github.com/zht7063/follow-books).
- Branch: `feat/thedankoe-ebook-prototype`.
- Unchanged base/main snapshot: `946dd3c94564d39b6c7ee4ff3ac00341ed9cd1c8`.
- Validated implementation HEAD SHA at report preparation: `9994622553c2377406e1242b751a2e2ed6dc83f2` ([commit](https://github.com/zht7063/follow-books/commit/9994622553c2377406e1242b751a2e2ed6dc83f2)). This report is a subsequent documentation-only commit; `git rev-parse HEAD` or the PR commits list gives the final tip including the report.
- PR: [#2 — Add an unofficial Dan Koe ebook reader and safe source collector](https://github.com/zht7063/follow-books/pull/2). Open into `main`, unmerged; auto-merge is disabled. **Do not merge unless asked.**
- Author: `Engineer (bot) <zht7063@users.noreply.github.com>`.
- Runner metadata supplied by the coordinator: **Codex CLI 0.163.0**, **gpt-6.1-sol**, reasoning effort **high**. This work was implemented by Codex in that run.
- No history rewriting, force-push, deployment, repository access change or five-person routine modification. Every file under `original-info/` remains unchanged.

## What was delivered

Seven original editorial chapters: orientation/identity, one-person business, writing/attention, AI/work, product history, unwatched videos and unread X references. The static reader has nine HTML pages, 63 source entries and 70 search entries. It includes a consistent contents rail, previous/next chapter navigation, original-source links, attribution, dates with provenance, independent fetch/read labels, clear coverage limits, a skip link, print rules and responsive CSS.

Search covers titles, tags, original editorial and clearly identified seed abstracts. X entries have URL text only in search and no seed summaries in published output. Videos remain unwatched. Company sources are attributed to Eden/Kortex with individual authorship unverified; the original seed attribution is retained separately for auditability.

The collector, builder and Python tests use the standard library; JavaScript uses the built-in Node test runner. No packages need installation. The builder never reads the raw cache.

## Collection results

Exact configured cap: **90 live HTTP attempts per invocation**, including robots, discovery, redirects and retries. Explicit finite plan: **25 URLs**. Actual request concurrency: **1**. Delay: **10 seconds** minimum, increased for robots delay/rate rules. User-Agent:

```text
FollowBooksResearch/0.1 (small personal research collector; contact: zht7063@users.noreply.github.com)
```

| Measure | Actual count |
| --- | ---: |
| Seed entries retained | 63 |
| Newly added catalog entries beyond the seed | 0 |
| Live HTTP attempts | 17 |
| Successful HTTP responses | 16 |
| Cache-hit events in the live ledger | 0 |
| Request-skip events in the live ledger | 0 |
| Restriction/block events | 1 |
| Transient network errors or backoff events | 0 |
| Catalog source entries fetched successfully | 11 |
| Source entries never requested | 51 |
| Sources reviewed, including partial excerpts | 3 |
| Complete public pages reviewed | 1 |
| Unreviewed/unwatched entries retained | 60 |
| X URL-only references retained | 12 |
| YouTube channel/video/playlist/RSS references, all unwatched | 8 |

Counts are deliberately separate: the 16 successful responses include two robots files and three discovery documents, as well as 11 catalog sources. The blocked source is a separate twelfth requested catalog entry. The 51 unrequested entries include URL duplicates and items outside the finite plan; they are source-entry counts, not unique request counts. Zero request-skip events does not mean all 63 sources were requested. Notes on each unrequested entry explain the policy/stop boundary. The 60 unreviewed entries include eight fetched-but-unreviewed sources, one blocked source and 51 unrequested entries. Two of the three reviewed sources were only opening excerpts, not complete essay reviews.

Hosts actually touched: **`thedankoe.com` and `letters.thedankoe.com` only**. No X, YouTube, Eden, Kortex, GitHub-content or third-party-site collection occurred.

At attempt 17, [This prompt will change your life](https://letters.thedankoe.com/p/this-prompt-will-change-your-life) returned **HTTP 200** with the marker **“this post is for paid subscribers”**. The collector immediately persisted a global stop. It did not retry the page or proceed to any remaining host. No HTTP request appears after the block event in the ledger. Later invocations against the stopped state made zero requests; subsequent review metadata was exported using the offline `--export-only` mode.

Machine-readable evidence: [collection-summary.json](../data/thedankoe/collection-summary.json) and [request-ledger.json](../data/thedankoe/request-ledger.json). Raw cache and resume state are local and gitignored.

## What was actually read

| Source | Review performed this run | Use in editorial |
| --- | --- | --- |
| [Dan's homepage](https://thedankoe.com/) (`site-01`) | Reviewed the public homepage, including identity and project links | Identity, author/business context |
| [How I'd build a one-person business](https://letters.thedankoe.com/p/how-id-build-a-one-person-business) (`letter-04`) | First 14,000 characters of locally extracted page text; remaining text unreviewed | Learning format versus underlying need, interactive guidance and adaptation |
| [The Future Of Work (Acquire This Skill Stack)](https://thedankoe.com/letters/the-future-of-work-acquire-this-skill-stack/) (`letter-12`) | First 14,000 characters of locally extracted page text; remaining text unreviewed | Generalist learning and experimentation; predictions explicitly treated as attributed claims |

Review notes are bound to exact cache hashes in [reviewed-sources.json](../editorial/thedankoe/reviewed-sources.json). A later source change cannot silently inherit a review label.

Fetched but **not newly reviewed**: `site-03`, `letter-01`, `letter-02`, `letter-03`, `letter-05`, `letter-09`, `letter-10` and `letter-11`. Their previous seed abstracts remain labelled as earlier curation, not fresh summaries. The blocked `letter-06` was not reviewed or unlocked. All remaining catalog entries are seed-only/unread/unwatched as individually recorded.

Discovery responses: robots for each touched host; the personal-site sitemap index; the newsletter RSS feed and sitemap. Only discovery structure was inspected, not every linked article or RSS body. A sitemap modification date was not used as an article publication date. The original seed dates and their explanations are preserved, including unknown dates and the X account-creation date.

## Gaps and identity discrepancies

The seed selected software, AI and digital-product topics. This prototype adds an editorial reading structure and limited new review, **not a broader corpus census**. It does not cover all mindset/growth writing, exhaust newsletter archives, reconcile every mirrored letter, enumerate all product blog posts or scan the large X timeline. Historical seed counts of roughly 93 Substack and 189 WordPress letters, and 192 Eden blog titles, remain prior survey context; this run does not claim to have read those corpora.

The seed README/RSS reference contains channel ID `UCWXYDYv5STLk-zoxMP2I1Lw`, while the seed CSV's channel identity row contains `UCswG6FSbgZjbWtdf_hMLaow`. **Unresolved:** the live stop occurred before channel-page or official RSS verification. Neither candidate was silently selected as correct. The conflict is visible on the homepage and video chapter. No videos were watched, and no transcripts were collected.

Eden and Kortex were not reached after the stop. The historical Kortex-to-Eden relationship and sunset description are explicitly attributed to the seed. Current redirects, availability, product behavior and feature claims were not verified this run. No course purchase, PDF/book download, signup or account use occurred.

## Reproduce and validate

Runtime used: Python 3.13.5 and Node v24.22.1. There are no third-party dependencies to install.

```bash
# Offline plan, no network or file writes
python3 scripts/collect_thedankoe.py

# Live mode is optional, bounded, and respects the persistent stop
python3 scripts/collect_thedankoe.py --live --budget 90 --delay 10

# Offline metadata export, only if local raw/state already exists
python3 scripts/collect_thedankoe.py --export-only

# Build and checks; all default tests are offline
npm run build
npm run check
npm test
python3 scripts/validate_content.py

# Local static preview of published output only
python3 -m http.server 4173 --bind 127.0.0.1 --directory site
```

The supplied stopped state must not be deleted to work around the restriction. A fresh clone does not contain copyrighted cache bodies or private resume state and can build/test without them. Explicit stale-age refresh is available only for an unblocked run; it does not override a stop. The public code has no concurrency option and no browser/authentication path.

| Verification | Result |
| --- | --- |
| `npm run build` | PASS — 9 HTML pages, 63 sources, 70 search entries |
| `npm run check` | PASS — Node syntax and Python compilation |
| `npm test` | PASS — **27 Python tests + 7 Node tests**, zero failures |
| `python3 scripts/validate_content.py` | PASS — 63 sources and 12 published/editorial files checked against available raw cache |
| Strict frontend static audit | PASS — zero findings; [evidence](design-audit.json) |
| Restriction-guard mutation check | PASS — inverted status guard caused 11 assertion failures; original restored; [evidence](mutation-check.json) |
| Independent code review/re-review | Two collector safety findings fixed; re-review found no remaining actionable P1/P2 issues |
| Local HTTP smoke | PASS — six endpoints returned 200; [evidence](preview-smoke.json) |
| Staged-file checks | PASS — no raw cache, credential material or archive changes |
| GitHub Actions at validated implementation SHA | PASS — push run [44499612164](https://github.com/zht7063/follow-books/actions/runs/44499612164) and PR run [44499665850](https://github.com/zht7063/follow-books/actions/runs/44499665850) |

Offline collector fixtures cover immediate persistent stops on restricted statuses, captcha, login/paywall and account redirects; serial cache/dedup/resume; robots disallow/delay; network/5xx-only bounded backoff; finite budgets; cache integrity; and explicit stale refresh. Review found that oversized/erroring bodies could hide restricted statuses and that NaN could bypass the delay floor. The fixes check restricted status before any body read, scan bounded body chunks, stop on oversized uninspectable responses, and reject nonfinite settings. Transport-level mocked-opener fixtures verify those paths.

Publication checks cover metadata/date provenance and preserved seed IDs, company attribution, resolved page/anchor links, search consistency, deterministic builds, contrast tokens, semantic markup, 375px CSS contracts, and real gitignore behavior. Node DOM fixtures exercise search restoration/clear/focus, IME composition, no results and failed index loading. **No browser GUI was driven**; these checks are not screenshots or a complete rendered-layout/accessibility audit.

## Preview and external hosting limit

The dedicated preview is intentionally left running:

- URL: **http://127.0.0.1:4173/**.
- PID: **2321421**.
- Port: **4173**.
- Bind: **127.0.0.1**.
- Served directory: `/workspace/engineer/follow-books/site`.
- Started: `2026-11-19T09:44:43+00:00`.
- Command: `python3 -m http.server 4173 --bind 127.0.0.1 --directory site`.
- Local ignored log: `.cache/preview.log`.
- Machine-readable record: [preview-server.json](preview-server.json).

This is loopback on the implementation machine, **not a public remote URL**. GitHub Pages is not enabled. Making an external preview available would require a separately authorized hosting or forwarding step. This run did not enable Pages or create/change Vercel, Cloudflare, DNS, domains, visibility, collaborator access or paid services.

## Copyright and remaining limits

Only normalized metadata, source links, short previously curated seed abstracts and original editorial are committed. No full article bodies, books, course materials, videos, transcripts, cookies, tokens or secrets are published. Raw HTML/XML and local state are gitignored. The published build is served from `site/` alone.

The hygiene guard flags a contiguous overlap of 40 normalized tokens with at least 200 characters between local raw cache and published/editorial files. Fixtures demonstrate that a long copied passage fails and a short quote passes. This is a practical regression guard, not an assessment of close paraphrase, translation, cumulative quotation or legal permission. This edition uses no intentional article quotations beyond source titles. Reading exercises and interpretations are clearly editorial; author claims are not independently verified financial, employment or product claims.

The implementation remains a prototype with static evidence for mobile/accessibility behavior, incomplete source coverage, unresolved channel identity, and no external hosting. These limits are stated in the reader itself.
