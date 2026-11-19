"""Offline importer fixtures contain public quotes and synthetic filler only.

No actual full 200+ character post or long article is vendored in tests.
"""
import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.import_x_sample import (AUTHOR, EXCLUSIONS, QUERY, SELECTION, normalize,
                                    read_json, singapore_time, validate_coverage,
                                    validate_sources, write_import)

ROOT = Path(__file__).resolve().parents[1]
TEST_CACHE = ROOT / '.cache/tests'
TEST_CACHE.mkdir(parents=True, exist_ok=True)
# Frozen facts from the official created_at and UTF-8 text, not fetch-time dates.
FACTS = [
    ('2026-11-14T16:07:37.000Z', '2026-11-15 00:07:37 +08 (Asia/Singapore)', 68, '6ab200dad1a6350310412724e4615b7bb008788c3f3e73244a4868ff1fbbabc6'),
    ('2026-11-05T16:57:10.000Z', '2026-11-06 00:57:10 +08 (Asia/Singapore)', 266, 'dc4accb28f63e3ae5c2446020eaab43580f6b9af386c445605ee04b476f276ea'),
    ('2026-11-17T15:44:24.000Z', '2026-11-17 23:44:24 +08 (Asia/Singapore)', 263, '129b53b8768c0f3d6b00203b43d0aa81a54ccbb51e60fc22b2824703e55b5b22'),
    ('2026-11-08T16:15:46.000Z', '2026-11-09 00:15:46 +08 (Asia/Singapore)', 277, '48fd6ef9163ddefde2c2141e2383a16c9fa52631433886e3d08a7bace17403be'),
    ('2026-10-30T13:15:19.000Z', '2026-10-30 21:15:19 +08 (Asia/Singapore)', 205, '5450aacc7456ed70ae9d0eecdedbf3a66930086df8187d42dfdb4bc8052c165a'),
]


def fixtures():
    public = read_json(ROOT / 'data/thedankoe/sample-sources.json')
    selected, posts = [], []
    for source, (_, quote) in zip(public, SELECTION):
        # Explicitly artificial text. Preserves punctuation/Unicode/hash tests,
        # without placing complete real posts in a committed fixture.
        text = quote if source['fetched_text_length'] == 68 else quote + ' SYNTHETIC fixture: café, 例子; not an actual post.'
        post = {'id': source['post_id'], 'text': text, 'author_id': AUTHOR['id'],
                'conversation_id': source['post_id'], 'display_text_range': [0, len(text)],
                'created_at': source['created_at'], 'lang': 'en', 'url': source['url']}
        posts.append(post)
        selected.append({**post, 'post_id': post['id'], 'sample_id': source['id'],
                         'author_name': AUTHOR['name'], 'author_username': AUTHOR['username'],
                         'text_sha256': hashlib.sha256(text.encode()).hexdigest(),
                         'fetched_text_length': len(text), 'created_at_singapore': source['created_at_singapore'],
                         'completeness': 'complete_short_post', 'same_as_conversation': True,
                         'note_post': None, 'has_article': False})
    for index, (post_id, reason, _) in enumerate(EXCLUSIONS):
        post = {'id': post_id, 'author_id': AUTHOR['id'], 'text': 'Synthetic unfinished preview',
                'display_text_range': [0, 28]}
        if reason == 'long_article':
            entry = read_json(ROOT / 'data/thedankoe/sample-coverage.json')['exclusions'][index]
            post['article'] = {'title': entry['title'], 'plain_text': 'S' * entry['plain_len']}
        if reason == 'unfetched_link':
            post['entities'] = {'urls': [{'url': 'https://example.invalid/not-fetched'}]}
            post['display_text_range'] = [0, 8]
        posts.append(post)
    return {
        'search-posts-all-01.json': {'tool': 'x.search_posts_all', 'namespace': 'x',
                                   'result': {'meta': {'result_count': 0}}, 'http_outcome': 'success_empty', 'restriction': False},
        'search-posts-all-02.json': {'tool': 'x.search_posts_all', 'namespace': 'x', 'query': QUERY,
                                   'max_results': 10, 'queried_at': public[0]['provenance']['queried_at'],
                                   'response': {'meta': {'result_count': 10}, 'data': posts,
                                                'includes': {'users': [dict(AUTHOR)]}}},
        'selected-sample-posts.json': {'selected_for_sample': selected},
    }


def write_fixtures(directory, documents):
    for name, value in documents.items():
        (directory / name).write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')


class ImportTests(unittest.TestCase):
    def test_committed_facts_preserve_hash_length_and_official_dates(self):
        sources = read_json(ROOT / 'data/thedankoe/sample-sources.json')
        validate_sources(sources)
        for source, (utc, display, length, digest) in zip(sources, FACTS):
            self.assertEqual((source['created_at'], source['created_at_singapore'],
                              source['fetched_text_length'], source['content_hash']['value']),
                             (utc, display, length, digest))
            self.assertEqual(source['provenance']['date_field'], 'created_at (UTC)')
            self.assertEqual(singapore_time(utc), display)

    def test_fixture_import_is_deterministic_offline_and_hashes_utf8(self):
        docs = fixtures()
        with tempfile.TemporaryDirectory(dir=TEST_CACHE) as directory:
            root = Path(directory)
            write_fixtures(root, docs)
            with patch('socket.socket', side_effect=AssertionError('Network forbidden')):
                sources, coverage = write_import(root, root / 'public')
                before = {p.name: p.read_bytes() for p in (root / 'public').iterdir()}
                write_import(root, root / 'public')
            self.assertEqual(before, {p.name: p.read_bytes() for p in (root / 'public').iterdir()})
            for source, saved in zip(sources, docs['selected-sample-posts.json']['selected_for_sample']):
                self.assertEqual(source['content_hash']['value'], hashlib.sha256(saved['text'].encode('utf-8')).hexdigest())
                self.assertEqual(source['fetched_text_length'], len(saved['text']))
                self.assertEqual(source['quote'], next(q for p, q in SELECTION if p == source['post_id']))
            validate_coverage(coverage, sources)
            text = ''.join(p.read_text() for p in (root / 'public').iterdir())
            self.assertNotIn('SYNTHETIC', text)
            self.assertNotIn('S' * 200, text)
            self.assertEqual(coverage['official_result_count'], 10)
            self.assertEqual(coverage['selected_count'], 5)

    def test_missing_file_fails_without_writing_or_network(self):
        for missing in fixtures():
            with self.subTest(missing=missing), tempfile.TemporaryDirectory(dir=TEST_CACHE) as directory:
                root = Path(directory)
                write_fixtures(root, {k: v for k, v in fixtures().items() if k != missing})
                with patch('socket.socket', side_effect=AssertionError('Network forbidden')), self.assertRaises(FileNotFoundError):
                    write_import(root, root / 'public')
                self.assertFalse((root / 'public').exists())

    def test_import_rejects_corrupt_or_incomplete_selected_evidence(self):
        # Most mutations change both copies so cross-checking cannot hide a
        # missing actual completeness/hash/date/conversation check.
        for mutation in ('hash', 'length', 'date', 'range', 'unfinished', 'conversation', 'article',
                         'note_post', 'note_tweet', 'author', 'quote', 'response_disagrees', 'truncated_selection',
                         'result_count', 'initial_restriction', 'missing_date', 'wrong_username'):
            docs = fixtures()
            saved = docs['selected-sample-posts.json']['selected_for_sample'][1]
            post = docs['search-posts-all-02.json']['response']['data'][1]
            if mutation == 'hash': saved['text_sha256'] = 'f' * 64
            elif mutation == 'length': saved['fetched_text_length'] += 1
            elif mutation == 'date': saved['created_at_singapore'] = '2026-11-19 00:00:00 +08 (Asia/Singapore)'
            elif mutation == 'range': saved['display_text_range'] = post['display_text_range'] = [0, 12]
            elif mutation == 'unfinished':
                saved['text'] = post['text'] = post['text'][:-1]
                saved['display_text_range'] = post['display_text_range'] = [0, len(post['text'])]
                saved['fetched_text_length'] = len(post['text'])
                saved['text_sha256'] = hashlib.sha256(post['text'].encode()).hexdigest()
            elif mutation == 'conversation': saved['conversation_id'] = post['conversation_id'] = 'different'
            elif mutation == 'article': post['article'] = {'plain_text': 'Synthetic longform.'}
            elif mutation in ('note_post', 'note_tweet'): post[mutation] = {'text': 'Synthetic note.'}
            elif mutation == 'author': saved['author_id'] = post['author_id'] = '999'
            elif mutation == 'quote':
                saved['text'] = post['text'] = 'Synthetic replacement. Complete but quote missing.'
                saved['display_text_range'] = post['display_text_range'] = [0, len(post['text'])]
                saved['fetched_text_length'] = len(post['text'])
                saved['text_sha256'] = hashlib.sha256(post['text'].encode()).hexdigest()
            elif mutation == 'response_disagrees': saved['created_at'] = '2026-01-01T00:00:00.000Z'
            elif mutation == 'truncated_selection': saved['post_id'] = EXCLUSIONS[0][0]
            elif mutation == 'result_count': docs['search-posts-all-02.json']['response']['meta']['result_count'] = 9
            elif mutation == 'initial_restriction': docs['search-posts-all-01.json']['restriction'] = True
            elif mutation == 'missing_date':
                del saved['created_at']
                del post['created_at']
            else: docs['search-posts-all-02.json']['response']['includes']['users'][0]['username'] = 'other'
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory(dir=TEST_CACHE) as directory:
                root = Path(directory)
                write_fixtures(root, docs)
                with self.assertRaises((ValueError, KeyError)):
                    write_import(root, root / 'public')
                self.assertFalse((root / 'public').exists())

    def test_public_validation_rejects_fulltext_bad_quotes_or_metadata(self):
        for mutation in ('body', 'full_quote', 'invented_date', 'missing_author', 'completeness', 'long_article', 'hash', 'provenance'):
            sources = read_json(ROOT / 'data/thedankoe/sample-sources.json')
            source = sources[1]
            if mutation == 'body': source['text'] = 'Forbidden body'
            elif mutation == 'full_quote': source['quote'] = 'word ' * 100
            elif mutation == 'invented_date': source['created_at'] = '2026-01-01T00:00:00.000Z'
            elif mutation == 'missing_author': del source['author']
            elif mutation == 'completeness': source['completeness'] = 'preview'
            elif mutation == 'long_article': source['fetched_text_length'] = 20156
            elif mutation == 'hash': source['content_hash']['value'] = 'z' * 64
            else: source['provenance']['date_field'] = 'fetch date'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_sources(sources)

    def test_coverage_rejects_missing_exclusions_and_restriction_misreport(self):
        sources = read_json(ROOT / 'data/thedankoe/sample-sources.json')
        for mutation in ('missing_exclusion', 'selected_count', 'empty_query_is_restriction', 'article_body'):
            coverage = read_json(ROOT / 'data/thedankoe/sample-coverage.json')
            if mutation == 'missing_exclusion': coverage['exclusions'].pop()
            elif mutation == 'selected_count': coverage['selected_count'] = 63
            elif mutation == 'article_body': coverage['exclusions'][-1]['plain_text'] = 'Forbidden body'
            else: coverage['initial_search']['restriction'] = True
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_coverage(coverage, sources)

    def test_cli_missing_cache_fails_without_dumping_payload(self):
        with tempfile.TemporaryDirectory(dir=TEST_CACHE) as directory:
            result = subprocess.run(['python3', 'scripts/import_x_sample.py', '--raw-dir', directory,
                                     '--output-dir', str(Path(directory) / 'public')], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('Offline import failed (FileNotFoundError)', result.stderr)
            self.assertEqual(result.stdout, '')
