"""Historical collector/seed integrity, separate from the five-post reader."""
import copy
import csv
import io
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

from scripts.collect_thedankoe import Collector, export, seed_sources
from scripts.validate_content import matching_passage, validate_hygiene, validate_sources

ROOT = Path(__file__).resolve().parents[1]
TEST_CACHE = ROOT / '.cache/tests'
TEST_CACHE.mkdir(parents=True, exist_ok=True)


class LegacyMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = json.loads((ROOT / 'data/thedankoe/sources.json').read_text())
        cls.seed = list(csv.DictReader(io.StringIO((ROOT / 'original-info/thedankoe/index.csv').read_text())))

    def test_schema_dates_attribution_and_seed_ids(self):
        validate_sources(self.sources, self.seed)
        self.assertEqual(len(self.sources), 63)
        for mutation in ['missing', 'status', 'provenance', 'seed_ids', 'fulltext']:
            values = copy.deepcopy(self.sources)
            if mutation == 'missing': del values[0]['author']
            elif mutation == 'status': values[0]['fetch_status'] = 'read_everything'
            elif mutation == 'provenance': values[1]['date_provenance'] = None
            elif mutation == 'seed_ids': values[0]['seed_ids'] = []
            else: values[0]['article_body'] = 'not allowed'
            with self.subTest(mutation=mutation), self.assertRaises((AssertionError, TypeError)):
                validate_sources(values, self.seed)

    def test_export_binds_reviews_and_withholds_blocked_seed_notes(self):
        for matches in [True, False]:
            with self.subTest(matches=matches), tempfile.TemporaryDirectory(dir=TEST_CACHE) as directory:
                root = Path(directory)
                registry = root / 'editorial/thedankoe/reviewed-sources.json'
                registry.parent.mkdir(parents=True)
                registry.write_text((ROOT / 'editorial/thedankoe/reviewed-sources.json').read_text())
                sources = seed_sources()
                homepage = next(s for s in sources if s['id'] == 'site-01')
                blocked = next(s for s in sources if s['id'] == 'letter-06')
                c = Collector(root / 'raw', transport=lambda url: self.fail('Offline export made a transport call'))
                (c.raw / 'fixture.body').write_text('<title>Public fixture homepage</title>')
                registered_hash = json.loads(registry.read_text())['site-01']['content_hash']
                c.state['responses'][homepage['url']] = {
                    'fetch_status': 'fetched_ok', 'http_status': 200, 'cache_file': 'fixture.body',
                    'content_hash': registered_hash if matches else 'f' * 64,
                    'fetched_at': '2026-11-19T00:00:00+00:00', 'decision_note': 'Offline fixture'}
                c.state['responses'][blocked['url']] = {
                    'fetch_status': 'blocked', 'http_status': 200, 'decision_note': 'Paid marker fixture'}
                c.state['stop_reason'] = 'Paid marker fixture'
                with patch('scripts.collect_thedankoe.ROOT', root):
                    export(c, sources, {})
                    export(c, sources, {})  # Repeated exports must preserve valid review scopes.
                self.assertEqual(homepage['read_status'], 'public_page_reviewed' if matches else 'fetched_not_reviewed')
                self.assertEqual('review_note' in homepage, matches)
                saved = json.loads((root / 'data/thedankoe/sources.json').read_text())
                withheld = next(s for s in saved if s['id'] == 'letter-06')
                self.assertIsNone(withheld['seed_abstract'])
                self.assertIsNone(withheld['seed_verification'])
                self.assertEqual(withheld['read_status'], 'unread')
                if matches:
                    homepage['content_hash'] = 'e' * 64
                    with patch('scripts.collect_thedankoe.ROOT', root), self.assertRaises(AssertionError):
                        export(c, sources, {})

    def test_company_sources_do_not_assume_personal_authorship(self):
        for source in self.sources:
            host = urlsplit(source['url']).hostname
            if host in {'eden.so', 'www.eden.so', 'kortex.co', 'www.kortex.co'} and source['section'] != 'x':
                self.assertIn('(organization)', source['author'])
                self.assertIn('individual authorship not verified', source['attribution_note'])
                self.assertIn('seed_attribution', source)

    def test_hygiene_rejects_a_long_copy_but_allows_a_short_quote(self):
        raw = ' '.join(f'originalword{i}' for i in range(100))
        self.assertTrue(matching_passage(raw, '<p>' + raw + '</p>'))
        self.assertTrue(matching_passage(raw, '<p>' + raw.replace(' ', '</span> <span>') + '</p>'))
        short_quote = ' '.join(raw.split()[:12])
        self.assertFalse(matching_passage(raw, f'<blockquote>{short_quote}</blockquote><p>Our own commentary and attribution.</p>'))
        with tempfile.TemporaryDirectory(dir=TEST_CACHE) as directory:
            raw_dir = Path(directory) / 'raw'
            raw_dir.mkdir()
            (raw_dir / 'fake.body').write_text(raw)
            output = Path(directory) / 'output.html'
            output.write_text(raw)
            with self.assertRaises(AssertionError):
                validate_hygiene(raw_dir, [output])
            output.write_text(short_quote)
            validate_hygiene(raw_dir, [output])

    def test_runtime_design_tokens_match_documented_palette(self):
        design = (ROOT / 'DESIGN.md').read_text()
        css = (ROOT / 'web/reader.css').read_text()
        colors = dict(re.findall(r'^  (primary|background|surface|text|muted|border): "(#[a-fA-F0-9]{6})"', design, re.M))
        self.assertEqual(len(colors), 6)
        for key, value in colors.items():
            self.assertIn(f'--{key}: {value}', css)
        # WCAG normal-text contrast on both reading surfaces.
        def lum(value):
            channels = [int(value[i:i+2], 16)/255 for i in (1, 3, 5)]
            linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in channels]
            return sum(a*b for a,b in zip(linear, [.2126,.7152,.0722]))
        for fg in ('text', 'muted', 'primary'):
            for bg in ('surface', 'background'):
                a,b = sorted([lum(colors[fg]), lum(colors[bg])])
                self.assertGreaterEqual((b+.05)/(a+.05), 4.5, (fg, bg))

    def test_gitignore_ignores_raw_caches_and_secrets(self):
        paths = ['data/thedankoe/raw/test.body', 'data/thedankoe/raw/state.json', '.cache/test', '.env', '.env.local', 'auth.json', 'local.key']
        result = subprocess.run(['git', 'check-ignore', '--stdin'], input='\n'.join(paths), text=True, cwd=ROOT, capture_output=True, check=True)
        self.assertEqual(set(result.stdout.splitlines()), set(paths))

    def test_request_ledger_counts_and_forbidden_platform_absence(self):
        summary = json.loads((ROOT / 'data/thedankoe/collection-summary.json').read_text())
        ledger = json.loads((ROOT / 'data/thedankoe/request-ledger.json').read_text())
        self.assertEqual(summary['concurrency'], 1)
        self.assertLessEqual(summary['counts']['attempted'], 90)
        self.assertEqual(summary['counts']['attempted'], sum(e['kind'] == 'attempted' for e in ledger))
        self.assertEqual(summary['counts']['fetched'], sum(e['kind'] == 'fetched' for e in ledger))
        self.assertFalse(any('x.com' in e['url'] or '/watch?' in e['url'] for e in ledger if e['kind'] == 'attempted'))
        blocked = next((i for i,e in enumerate(ledger) if e['kind'] == 'blocked'), None)
        if blocked is not None:
            self.assertFalse(any(e['kind'] == 'attempted' for e in ledger[blocked+1:]))
