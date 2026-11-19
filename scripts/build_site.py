#!/usr/bin/env python3
"""Deterministic, dependency-free static reader. Never reads the raw cache."""
from __future__ import annotations
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = {'identity': 'Identity & official sites', 'letters': 'Selected letters',
            'products': 'Eden & historical Kortex', 'videos': 'Videos · unwatched', 'x': 'X · URL-only references'}


def esc(value):
    return html.escape(str(value), quote=True)


def load():
    sources = json.loads((ROOT / 'data/thedankoe/sources.json').read_text())
    summary = json.loads((ROOT / 'data/thedankoe/collection-summary.json').read_text())
    chapters = json.loads((ROOT / 'editorial/thedankoe/chapters.json').read_text())
    reviewed_path = ROOT / 'editorial/thedankoe/reviewed-sources.json'
    reviewed = json.loads(reviewed_path.read_text()) if reviewed_path.exists() else {}
    for source in sources:
        review = reviewed.get(source['id'])
        if review and review['content_hash'] == source['content_hash'] and source['fetch_status'] == 'fetched_ok':
            source['read_status'] = review['read_status']
            source['review_note'] = review['note']
    return sources, summary, chapters


FETCH_LABELS = {'fetched_ok': 'public page fetched', 'seed_only': 'seed metadata only', 'blocked': 'collection stopped', 'unread': 'not requested', 'unwatched': 'not requested', 'skipped': 'skipped per policy', 'error': 'fetch unsuccessful'}
READ_LABELS = {'public_page_reviewed': 'public page reviewed', 'public_excerpt_reviewed': 'opening excerpt reviewed', 'seed_abstract_only': 'seed abstract only', 'fetched_not_reviewed': 'not reviewed', 'unread': 'unread', 'unwatched': 'unwatched'}


def source_card(source):
    s = source
    date = f'{esc(s["date"])} · {esc(s["date_provenance"]["note"])}' if s['date'] else 'Date unknown · no publication date inferred'
    abstract = ''
    if s['section'] != 'x' and s.get('seed_abstract'):
        abstract = f'<details><summary>Previously curated seed abstract (Chinese)</summary><p lang="zh-Hans" class="seed-abstract">{esc(s["seed_abstract"])}</p><p class="meta">From the 2026-11-19 seed snapshot; this is not a new full-text review.</p></details>'
    title = 'X reference · ' + s['id'] if s['section'] == 'x' else s['title']
    review = f'<p class="meta">{esc(s["review_note"])}</p>' if s.get('review_note') else ''
    return f'''<article class="source" id="{esc(s['id'])}">
<span class="source-id">{esc(s['id'])}</span>
<h3>{esc(title)}</h3>
<p><span class="badge">Fetch: {esc(FETCH_LABELS[s['fetch_status']])}</span><span class="badge">Read: {esc(READ_LABELS[s['read_status']])}</span></p>
<p class="meta">Attribution: {esc(s['author'])} · {esc(s['attribution_note'])}<br>
Date: {date}<br>Provenance: {esc(s['date_provenance']['kind'] if s['date_provenance'] else 'none')} · seed {esc(', '.join(s['seed_ids']))}</p>
{review}{abstract}
<p><a href="{esc(s['canonical_url'])}" rel="noreferrer">Open original source</a> <span class="meta">{esc(s['canonical_url'])}</span></p>
<details><summary>Collection & attribution notes</summary><p class="meta">{esc(s['decision_note'])}<br>{esc(s['robots_note'])}<br>HTTP: {esc(s['http_status'] if s['http_status'] is not None else 'not requested')} · Fetched: {esc(s['fetched_at'] or 'not this run')}<br>Seed verification: {esc(s['seed_verification'])}</p></details>
</article>'''


def shell(title, body, chapters, current='', depth=0):
    prefix = '../' if depth else ''
    links = [('index.html', 'Contents', 'home')]
    links += [(f'chapters/{c["id"]}.html', c['nav_title'], c['id']) for c in chapters]
    links += [('catalog.html', 'Search & source index', 'catalog')]
    navigation = ''.join(f'<li><a href="{prefix}{url}"' + (' aria-current="page"' if key == current else '') + f'>{esc(label)}</a></li>' for url, label, key in links)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self'; base-uri 'none'; form-action 'self'">
<meta name="referrer" content="no-referrer"><meta name="description" content="An unofficial curated ebook reading prototype about Dan Koe. Original editorial, selected source links, and explicit coverage limits.">
<title>{esc(title)} · Dan Koe study edition · Follow Books</title><link rel="stylesheet" href="{prefix}assets/reader.css">
</head><body><a class="skip" href="#main">Skip to reading</a><div class="book">
<aside class="cover"><a class="brand" href="{prefix}index.html">follow books</a><p class="edition">Dan Koe / study edition</p>
<p class="about-edition">A small companion for reading about writing, work, and the tools between them.</p>
<nav class="contents" aria-label="Book contents"><ul>{navigation}</ul></nav><p class="meta">Unofficial · Incomplete<br>Seed edition: 19 Nov 2026</p></aside>
<div class="leaf"><main id="main">{body}</main><footer>Unofficial curated ebook reading prototype. Independent editorial by Engineer (bot), with source material attributed to its authors. No affiliation or endorsement. Read complete works at the original links.</footer></div></div></body></html>'''


def build(output=None):
    output = Path(output) if output else ROOT / 'site'
    sources, summary, chapters = load()
    by_id = {s['id']: s for s in sources}
    (output / 'chapters').mkdir(parents=True, exist_ok=True)
    (output / 'assets').mkdir(exist_ok=True)
    for name in ('reader.css', 'search.js', 'search-core.js'):
        shutil.copyfile(ROOT / 'web' / name, output / 'assets' / name)
    counts = summary['counts']
    reviewed = sum(s['read_status'] in {'public_page_reviewed', 'public_excerpt_reviewed'} for s in sources)
    retained = sum(s['read_status'] not in {'public_page_reviewed', 'public_excerpt_reviewed'} for s in sources)
    chapter_list = '<ol class="chapter-list">' + ''.join(f'<li><a href="chapters/{esc(c["id"])}.html">{esc(c["title"])}</a><p>{esc(c["description"])}</p></li>' for c in chapters) + '</ol>'
    identity = next(s for s in sources if s['id'] == 'site-01')
    identity_text = ('His public homepage identifies him as the author of The Art of Focus, an Eden co-founder, and a writer exploring the mind, the internet and the future.' if identity['read_status'] == 'public_page_reviewed' else 'The seed snapshot identifies him as the author of The Art of Focus and an Eden co-founder. This identity has not been reviewed from a live page in this edition.')
    body = f'''<p class="eyebrow">An independent reading companion</p><h1>Dan Koe,<br>in perspective.</h1>
<p class="deck">Writing, the one-person business, and AI. A guided route through selected sources, with room to think between the links.</p>
<div class="notice"><p><strong>Unofficial curated ebook reading prototype.</strong> This is original editorial and an index, not a Dan Koe book or a complete archive. No affiliation or endorsement.</p></div>
<a class="primary" href="chapters/{esc(chapters[0]['id'])}.html">Begin reading</a>
<dl class="stats"><div><dt>Seed entries</dt><dd>{len(sources)}</dd></div><div><dt>Sources fetched this run</dt><dd>{counts['sources_fetched_ok']}</dd></div><div><dt>Pages / excerpts reviewed</dt><dd>{reviewed}</dd></div><div><dt>Unreviewed / unwatched</dt><dd>{retained}</dd></div></dl>
<section class="prose"><h2>Who is Dan?</h2><p>{identity_text} <a href="{esc(identity['canonical_url'])}">Identity source: his homepage</a>.</p>
<h2>How to read this edition</h2><p>Follow the chapters in order for a guided route, or use the source index to find a theme. Each chapter is our own reading companion. Open the originals for the author's complete argument. Previous and next links keep your place in this short edition.</p>
<p>Source labels distinguish a successful fetch from an actual review. Seed abstracts are earlier Chinese editorial, retained as such. Unknown dates stay unknown; seed dates carry their original provenance. Company product pages are attributed separately from Dan's personal essays.</p></section>
<h2>Contents</h2>{chapter_list}
<section class="prose" id="coverage"><h2>The edges of the collection</h2><p>The 63-entry seed was selected for software, AI and digital products. It underrepresents Dan's wider work on writing, mindset and personal growth. Earlier surveys of newsletter sitemaps and the Eden blog were metadata surveys, not complete reading.</p>
<p>X is URL-only, unread and never re-fetched. All videos are unwatched; no transcripts were obtained. Partial prompts and list-only entries remain partial. This is one person's selected collection, not a five-person library or a life archive.</p>
<p>Live HTTP attempts: {counts['attempted']} (including robots and discovery); successful responses: {counts['fetched']}; restriction events: {counts['blocked']}. Crawl result: {esc(summary['stop_reason'] or 'Finite selected plan completed; no completeness claim')}.</p>
<p>YouTube channel discrepancy: the seed README names <code>UCWXYDYv5STLk-zoxMP2I1Lw</code>, while the CSV identity row names <code>UCswG6FSbgZjbWtdf_hMLaow</code>. {esc(summary['youtube_verification']['result'])}</p></section>'''
    (output / 'index.html').write_text(shell('Contents', body, chapters, 'home'))
    search_index = []
    for i, chapter in enumerate(chapters):
        parts = [f'<p class="eyebrow">Reading companion · Chapter {i+1} of {len(chapters)}</p>', f'<h1>{esc(chapter["title"])}</h1>', f'<p class="deck">{esc(chapter["description"])}</p>', '<p class="meta">By Engineer (bot) · Original editorial · Edition date: 2026-11-19 (not a source publication date)</p>', '<div class="prose">']
        for section in chapter['sections']:
            parts += [f'<h2>{esc(section["heading"])}</h2>']
            parts += [f'<p>{esc(p)}</p>' for p in section['paragraphs']]
        parts += ['</div><h2>Sources for this chapter</h2><p class="meta">Dates and status below apply to individual sources. Fetching a page does not establish every claim in it.</p>']
        parts += [source_card(by_id[sid]) for sid in chapter['source_ids']]
        previous = f'<a href="{chapters[i-1]["id"]}.html">Previous: {esc(chapters[i-1]["nav_title"])}</a>' if i else '<a href="../index.html">Previous: Contents</a>'
        following = f'<a href="{chapters[i+1]["id"]}.html">Next: {esc(chapters[i+1]["nav_title"])}</a>' if i+1 < len(chapters) else '<a href="../catalog.html">Next: Search & source index</a>'
        parts += [f'<nav class="pager" aria-label="Chapter pagination">{previous}{following}</nav>']
        (output / 'chapters' / f'{chapter["id"]}.html').write_text(shell(chapter['title'], ''.join(parts), chapters, chapter['id'], 1))
        text = ' '.join([chapter['description']] + [p for section in chapter['sections'] for p in [section['heading'], *section['paragraphs']]])
        search_index.append({'id': chapter['id'], 'kind': 'chapter', 'title': chapter['title'], 'text': text,
                             'tags': chapter['tags'], 'href': f'chapters/{chapter["id"]}.html'})
    catalog = '''<p class="eyebrow">The evidence behind the edition</p><h1>Search & source index</h1>
<p class="deck">Browse every seed entry, or search titles, tags and our editorial. Article full text is not indexed.</p>
<form id="search-form" role="search" novalidate hidden><label for="query">Search this edition</label><div class="search-controls"><input id="query" name="q" type="search" placeholder="Try writing, AI, Eden…" autocomplete="off"><button type="submit">Search</button><button type="button" id="clear-search" disabled hidden>Clear search</button></div></form>
<p id="search-status" role="status" aria-live="polite"></p><div id="search-results" hidden></div>
<noscript><p>JavaScript is off. All sources remain grouped below; use your browser's find command.</p></noscript>
<div id="browse-sources">'''
    for key, label in SECTIONS.items():
        catalog += f'<section id="section-{key}"><h2>{esc(label)}</h2>'
        for source in sources:
            if source['section'] != key:
                continue
            catalog += source_card(source)
            # X text/summary remains excluded even from the hidden search index.
            title = 'X reference · ' + source['id'] if key == 'x' else source['title']
            search_index.append({'id': source['id'], 'kind': 'source', 'title': title,
                                 'tags': [] if key == 'x' else source['tags'],
                                 'text': source['canonical_url'] if key == 'x' else source.get('seed_abstract') or '',
                                 'href': f'catalog.html#{source["id"]}'})
        catalog += '</section>'
    catalog += '</div><script type="module" src="assets/search.js"></script>'
    (output / 'catalog.html').write_text(shell('Search & source index', catalog, chapters, 'catalog'))
    (output / 'search-index.json').write_text(json.dumps(search_index, ensure_ascii=False, indent=2) + '\n')
    print(f'Built {len(chapters)+2} pages, {len(sources)} sources, {len(search_index)} search entries into {output.relative_to(ROOT) if output.is_relative_to(ROOT) else output}')


if __name__ == '__main__':
    build()
