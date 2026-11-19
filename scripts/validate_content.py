#!/usr/bin/env python3
"""Offline metadata and republication guards; these are heuristics, not legal judgments."""
import csv
import io
import html
import json
import re
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

if __package__:
    from .review_integrity import load_reviews, validate_review
else:
    from review_integrity import load_reviews, validate_review

ROOT = Path(__file__).resolve().parents[1]
FETCH_STATUSES = {'fetched_ok', 'skipped', 'blocked', 'unread', 'unwatched', 'seed_only', 'error'}
READ_STATUSES = {'unread', 'unwatched', 'seed_abstract_only', 'fetched_not_reviewed', 'public_page_reviewed', 'public_excerpt_reviewed'}
REQUIRED = {'id', 'seed_ids', 'title', 'url', 'canonical_url', 'date', 'date_provenance', 'author',
            'attribution_note', 'source_type', 'tags', 'section', 'fetch_status', 'read_status',
            'http_status', 'content_hash', 'fetched_at', 'robots_note', 'decision_note'}


def validate_sources(sources, seed_rows):
    reviews = load_reviews(ROOT)
    expected = {r['id']: r for r in seed_rows}
    ids = [s['id'] for s in sources]
    assert len(ids) == len(set(ids)), 'Duplicate source id'
    assert set(ids) == set(expected), 'All 63 seed ids must be preserved exactly'
    for s in sources:
        assert REQUIRED <= s.keys(), f'Missing fields on {s.get("id")}'
        assert s['seed_ids'] == [s['id']], 'Lost seed relationship'
        assert s['fetch_status'] in FETCH_STATUSES, 'Invalid fetch status'
        assert s['read_status'] in READ_STATUSES, 'Invalid read status'
        assert s['section'] in {'identity', 'letters', 'products', 'videos', 'x'}
        assert s['author'] and s['source_type'] and isinstance(s['tags'], list)
        assert s['date'] == (expected[s['id']]['日期'] or None), 'Seed date changed'
        if s['date']:
            date.fromisoformat(s['date'])
            p = s['date_provenance']
            assert p and p['kind'] == 'seed' and p['seed_id'] == s['id'] and p['note'], 'Date lacks provenance'
        else:
            assert s['date_provenance'] is None, 'Unknown date must have no invented provenance'
        if s['content_hash']:
            assert re.fullmatch('[a-f0-9]{64}', s['content_hash'])
        if s['fetch_status'] == 'fetched_ok':
            assert s['http_status'] and 200 <= s['http_status'] < 300 and s['content_hash'] and s['fetched_at']
        if s['section'] == 'x':
            assert s['fetch_status'] == 'unread' and s['read_status'] == 'unread' and s['seed_abstract'] is None
            assert s['http_status'] is None, 'No X requests allowed'
        if s['section'] == 'videos':
            assert s['read_status'] == 'unwatched'
        validate_review(s, reviews)
        if s['fetch_status'] == 'blocked':
            assert s.get('seed_abstract') is None and not s.get('seed_verification'), 'Blocked seed notes must be withheld'
        assert not {'body', 'html', 'content', 'article_body', 'transcript'} & s.keys(), 'Raw body in metadata'


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style'}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {'script', 'style'}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def words(content):
    parser = VisibleText()
    parser.feed(html.unescape(content))
    return re.findall(r'[a-z0-9]+|[\u3400-\u9fff]', ' '.join(parser.parts).lower())


def matching_passage(raw, published, window=40, min_chars=200):
    """Flag a contiguous 40-token verbatim overlap of at least 200 characters.

    Case/markup/punctuation insensitive. This catches copied passages, including
    escaped HTML. It deliberately allows short quotes and titles. It does not
    assess close paraphrase, translation or cumulative quotation limits.
    """
    raw_words, published_words = words(raw), words(published)
    windows = {tuple(raw_words[i:i + window]) for i in range(len(raw_words) - window + 1)
               if sum(map(len, raw_words[i:i + window])) >= min_chars}
    return any(tuple(published_words[i:i + window]) in windows for i in range(len(published_words) - window + 1))


def validate_hygiene(raw_dir, published_files):
    raw_files = list(Path(raw_dir).glob('*.body'))
    # Per-file comparisons prevent arbitrary coincidences across unrelated articles.
    for path in published_files:
        content = path.read_text(errors='replace')
        for raw_path in raw_files:
            assert not matching_passage(raw_path.read_text(errors='replace'), content), f'Long verbatim overlap: {path} vs local cache hash {raw_path.stem}'


def main():
    sources = json.loads((ROOT / 'data/thedankoe/sources.json').read_text())
    rows = list(csv.DictReader(io.StringIO((ROOT / 'original-info/thedankoe/index.csv').read_text())))
    validate_sources(sources, rows)
    files = list((ROOT / 'site').rglob('*.html')) + [ROOT / 'site/search-index.json'] + list((ROOT / 'editorial/thedankoe').glob('*.json'))
    validate_hygiene(ROOT / 'data/thedankoe/raw', files)
    print(f'Validated {len(sources)} sources and {len(files)} published/editorial files; raw caches stay local.')


if __name__ == '__main__':
    main()
