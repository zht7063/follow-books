import copy
import csv
import io
import json
import re
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from scripts.build_site import build
from scripts.validate_content import matching_passage, validate_hygiene, validate_sources

ROOT = Path(__file__).resolve().parents[1]
TEST_CACHE = ROOT / '.cache/tests'
TEST_CACHE.mkdir(parents=True, exist_ok=True)


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.ids = []
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag in {'a', 'link', 'script'}:
            self.links.append(attrs.get('href') or attrs.get('src'))


class PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = json.loads((ROOT / 'data/thedankoe/sources.json').read_text())
        cls.seed = list(csv.DictReader(io.StringIO((ROOT / 'original-info/thedankoe/index.csv').read_text())))
        cls.chapters = json.loads((ROOT / 'editorial/thedankoe/chapters.json').read_text())

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

    def test_company_sources_do_not_assume_personal_authorship(self):
        for source in self.sources:
            host = urlsplit(source['url']).hostname
            if host in {'eden.so', 'www.eden.so', 'kortex.co', 'www.kortex.co'} and source['section'] != 'x':
                self.assertIn('(organization)', source['author'])
                self.assertIn('individual authorship not verified', source['attribution_note'])
                self.assertIn('seed_attribution', source)

    def test_all_sources_have_a_chapter_and_search_entry(self):
        ids = {s['id'] for s in self.sources}
        chapter_source_ids = [sid for c in self.chapters for sid in c['source_ids']]
        self.assertEqual(set(chapter_source_ids), ids)
        self.assertEqual(len(chapter_source_ids), len(ids))
        search = json.loads((ROOT / 'site/search-index.json').read_text())
        self.assertEqual({s['id'] for s in search if s['kind'] == 'source'}, ids)
        self.assertEqual({s['id'] for s in search if s['kind'] == 'chapter'}, {c['id'] for c in self.chapters})
        self.assertEqual(len(search), len(ids) + len(self.chapters))
        for entry in search:
            parts = urlsplit(entry['href'])
            target = ROOT / 'site' / parts.path
            self.assertTrue(target.exists(), entry)
            if parts.fragment:
                self.assertIn(parts.fragment, Page(target.read_text()).ids)

    def test_all_links_resolve_and_pages_have_landmarks_and_disclaimer(self):
        site = ROOT / 'site'
        pages = list(site.rglob('*.html'))
        self.assertEqual(len(pages), len(self.chapters) + 2)
        for path in pages:
            text = path.read_text()
            page = Page(text)
            self.assertEqual(len(page.ids), len(set(page.ids)), path)
            self.assertIn('Unofficial curated ebook reading prototype', text)
            self.assertIn('No affiliation or endorsement', text)
            self.assertTrue(any(t == 'main' for t, _ in page.tags))
            self.assertTrue(any(t == 'html' and a['lang'] == 'en' for t, a in page.tags))
            self.assertIn('#main', page.links)
            self.assertTrue(any(t == 'meta' and a.get('name') == 'viewport' for t, a in page.tags))
            for href in page.links:
                if not href: continue
                parts = urlsplit(href)
                if parts.scheme:
                    self.assertEqual(parts.scheme, 'https')
                    continue
                target = (path.parent / unquote(parts.path)).resolve() if parts.path else path.resolve()
                self.assertTrue(target.is_relative_to(site.resolve()), href)
                self.assertTrue(target.is_file(), f'{path}: {href}')
                if parts.fragment:
                    self.assertIn(parts.fragment, Page(target.read_text()).ids)
        for i, chapter in enumerate(self.chapters):
            text = (site / 'chapters' / f'{chapter["id"]}.html').read_text()
            self.assertIn('aria-label="Chapter pagination"', text)
            self.assertIn('Previous:', text)
            self.assertIn('Next:', text)
            self.assertIn('aria-current="page"', text)

    def test_deterministic_offline_build(self):
        with tempfile.TemporaryDirectory(dir=TEST_CACHE) as directory:
            output = Path(directory)
            build(output)
            for path in output.rglob('*'):
                if path.is_file():
                    self.assertEqual(path.read_bytes(), (ROOT / 'site' / path.relative_to(output)).read_bytes())

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

    def test_actual_publication_against_available_local_caches(self):
        files = list((ROOT / 'site').rglob('*.html')) + [ROOT / 'site/search-index.json'] + list((ROOT / 'editorial/thedankoe').glob('*.json'))
        validate_hygiene(ROOT / 'data/thedankoe/raw', files)

    def test_no_x_summaries_or_video_viewing_claims_in_output(self):
        search = json.loads((ROOT / 'site/search-index.json').read_text())
        for source in self.sources:
            if source['section'] == 'x':
                entry = next(e for e in search if e['id'] == source['id'])
                self.assertEqual(entry['text'], source['canonical_url'])
                self.assertEqual(entry['tags'], [])
            if source['section'] == 'videos':
                self.assertEqual(source['read_status'], 'unwatched')
        home = (ROOT / 'site/index.html').read_text()
        self.assertIn('UCWXYDYv5STLk-zoxMP2I1Lw', home)
        self.assertIn('UCswG6FSbgZjbWtdf_hMLaow', home)
        self.assertIn('Unresolved', home)

    def test_small_viewport_css_and_search_semantic_contracts(self):
        css = (ROOT / 'web/reader.css').read_text()
        self.assertIn('max-width: 66ch', css)
        self.assertIn('min-width: 0', css)
        self.assertIn('@media (max-width: 760px)', css)
        self.assertIn('.book { display: block; padding: 1rem; }', css)
        self.assertIn('.contents ul { display: flex; flex-wrap: wrap', css)
        self.assertIn('overflow-wrap: anywhere', css)
        self.assertIn(':focus-visible', css)
        self.assertIn('forced-colors: active', css)
        self.assertIn('prefers-reduced-motion: reduce', css)
        self.assertNotRegex(css, r'(?<!max-)\bwidth:\s*(?:[4-9]\d\d|\d{4,})px')
        self.assertNotIn('overflow-x: hidden', css)
        # At 375px the <=400px branch leaves 359px outer width, with
        # 325px inside the 1rem leaf padding and border. No fixed width overrides it.
        self.assertGreaterEqual(375 - 2 * 8 - 2 * 16 - 2, 320)
        catalog = (ROOT / 'site/catalog.html').read_text()
        for text in ['role="search"', 'for="query"', 'id="clear-search"', 'role="status"', '<noscript>']:
            self.assertIn(text, catalog)

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
