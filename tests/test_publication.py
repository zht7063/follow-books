import copy
import json
import re
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

from scripts.build_site import CHAPTER_FILE, LEGACY_FILES, build, load, source_note
from scripts.import_x_sample import EXCLUSIONS, read_json
from scripts.validate_content import matching_passage, validate_hygiene

ROOT = Path(__file__).resolve().parents[1]
TEST_CACHE = ROOT / '.cache/tests'
TEST_CACHE.mkdir(parents=True, exist_ok=True)


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.ids, self.tags = [], [], []
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
        cls.sources, cls.coverage, cls.chapter = load()

    def test_home_is_a_chinese_sample_with_upfront_coverage(self):
        home = (ROOT / 'site/index.html').read_text()
        for expected in ('从开始到专注', '非官方', '未完成', '不是完整书籍或人物传记', 'Engineer (bot)',
                         '10 条结果', '5 条完整短帖', '成功空结果', '尚未获得用户视觉验收', '交付此小样后停止', CHAPTER_FILE):
            self.assertIn(expected, home)
        for excluded_id, _, _ in EXCLUSIONS:
            self.assertIn(excluded_id, home)
        for obsolete in ('Who is Dan?', 'Dan Koe,<br>in perspective.', 'Search & source index', 'catalog.html'):
            self.assertNotIn(obsolete, home)

    def test_five_continuous_passages_distinguish_editorial_quote_and_source(self):
        text = (ROOT / 'site' / CHAPTER_FILE).read_text()
        self.assertEqual(text.count('class="passage"'), 5)
        self.assertEqual(text.count('>编辑整理</p>'), 5)
        self.assertEqual(text.count('>短引文 · 原文节选</p>'), 5)
        self.assertEqual(text.count('>来源</p>'), 5)
        self.assertEqual(text.count('<blockquote lang="en">'), 5)
        self.assertIn('不是逐句翻译', text)
        self.assertIn('不按发表时间排列', text)
        for passage, source in zip(self.chapter['passages'], self.sources):
            self.assertEqual(passage['source_id'], source['id'])
            self.assertGreaterEqual(len(passage['paragraphs']), 2)
            self.assertIn(source_note(source), text)
        for post_id, _, _ in EXCLUSIONS:
            self.assertNotIn(post_id, text)

    def test_every_source_shows_attribution_date_hash_provenance_and_completeness(self):
        for source in self.sources:
            text = source_note(source)
            for expected in (source['url'], 'DAN KOE', '@thedankoe', '256523056', source['created_at'],
                             source['created_at_singapore'], 'created_at（UTC）', source['content_hash']['value'],
                             'complete_short_post', 'display_text_range', '独立短帖', 'x.search_posts_all',
                             'search-posts-all-02.json', 'selected-sample-posts.json', '不声称读取了回复'):
                self.assertIn(expected, text)
            self.assertIn(str(source['fetched_text_length']) + ' 字符', text)
            self.assertLessEqual(len(source['quote']), 120)
            self.assertLessEqual(len(source['quote'].split()), 25)
            self.assertLessEqual(len(source['quote']), source['fetched_text_length'])
            if source['fetched_text_length'] > 68:
                self.assertLess(len(source['quote']), source['fetched_text_length'])

    def test_coverage_names_all_exclusions_and_unused_seed(self):
        text = (ROOT / 'site/coverage.html').read_text()
        for entry in self.coverage['exclusions']:
            self.assertIn(entry['post_id'], text)
            self.assertIn(entry['note'], text)
            if 'plain_len' in entry:
                self.assertIn(str(entry['plain_len']), text)
                self.assertIn(entry['title'], text)
        for expected in ('句中截断', '链接目标未取得', '长 X 文章', '旧 63 条种子目录', '非本样章素材', '没有翻页或增加来源',
                         '重新部署另行进行', '尚未获得用户视觉验收', '不扩充来源'):
            self.assertIn(expected, text)
        self.assertEqual(len(self.coverage['selected_ids']), 5)
        self.assertTrue(set(self.coverage['selected_ids']).isdisjoint(e['post_id'] for e in self.coverage['exclusions']))

    def test_links_resolve_and_all_pages_have_accessible_landmarks(self):
        site = ROOT / 'site'
        pages = list(site.rglob('*.html'))
        self.assertEqual({p.relative_to(site).as_posix() for p in pages}, {'index.html', CHAPTER_FILE, 'coverage.html'})
        for path in pages:
            text = path.read_text()
            page = Page(text)
            self.assertEqual(len(page.ids), len(set(page.ids)), path)
            for required in ('非官方', '未完成', 'No affiliation or endorsement', 'aria-current="page"', 'width=device-width'):
                self.assertIn(required, text)
            self.assertTrue(any(t == 'html' and a['lang'] == 'zh-Hans' for t, a in page.tags))
            self.assertTrue(any(t == 'main' and a['id'] == 'main' for t, a in page.tags))
            self.assertIn('#main', page.links)
            self.assertFalse(any(t == 'script' for t, _ in page.tags))
            for href in page.links:
                self.assertTrue(href)
                parts = urlsplit(href)
                if parts.scheme:
                    self.assertEqual(parts.scheme, 'https')
                    self.assertEqual(parts.hostname, 'x.com')
                    continue
                target = (path.parent / unquote(parts.path)).resolve() if parts.path else path.resolve()
                self.assertTrue(target.is_relative_to(site.resolve()), href)
                self.assertTrue(target.is_file(), (path, href))
                if parts.fragment:
                    self.assertIn(parts.fragment, Page(target.read_text()).ids)
        chapter = (site / CHAPTER_FILE).read_text()
        self.assertIn('上一页：样章首页', chapter)
        self.assertIn('下一页：覆盖说明与编后记', chapter)

    def test_build_is_deterministic_without_reading_private_or_legacy_content(self):
        original = Path.read_text
        def public_only(path, *args, **kwargs):
            self.assertFalse(path.is_relative_to(ROOT / 'data/thedankoe/raw'), path)
            self.assertNotIn(path.name, ('sources.json', 'chapters.json', 'collection-summary.json'))
            return original(path, *args, **kwargs)
        with tempfile.TemporaryDirectory(dir=TEST_CACHE) as directory:
            output = Path(directory)
            with patch.object(Path, 'read_text', public_only), patch('socket.socket', side_effect=AssertionError('Network forbidden')):
                build(output)
                first = {str(p.relative_to(output)): p.read_bytes() for p in output.rglob('*') if p.is_file()}
                build(output)
            committed = {str(p.relative_to(ROOT / 'site')): p.read_bytes() for p in (ROOT / 'site').rglob('*') if p.is_file()}
            self.assertEqual(first, committed)
            self.assertEqual(first, {str(p.relative_to(output)): p.read_bytes() for p in output.rglob('*') if p.is_file()})

    def test_rebuild_removes_known_old_catalog_and_chapters(self):
        with tempfile.TemporaryDirectory(dir=TEST_CACHE) as directory:
            output = Path(directory)
            for name in LEGACY_FILES:
                target = output / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text('Obsolete generated catalog fixture')
            (output / 'unrelated.txt').write_text('Not owned by builder')
            build(output)
            self.assertFalse(any((output / name).exists() for name in LEGACY_FILES))
            self.assertEqual((output / 'unrelated.txt').read_text(), 'Not owned by builder')

    def test_invalid_source_or_editorial_fails_before_site_writes(self):
        for mutation in ('source_body', 'sixth_passage', 'excluded_post'):
            original = Path.read_text
            sources = copy.deepcopy(self.sources)
            chapter = copy.deepcopy(self.chapter)
            if mutation == 'source_body': sources[0]['article_body'] = 'Forbidden'
            elif mutation == 'sixth_passage': chapter['passages'].append(chapter['passages'][0])
            else: chapter['passages'][0]['source_id'] = EXCLUSIONS[0][0]
            def mutated(path, *args, **kwargs):
                if path == ROOT / 'data/thedankoe/sample-sources.json': return json.dumps(sources)
                if path == ROOT / 'editorial/thedankoe/sample-chapter.json': return json.dumps(chapter)
                return original(path, *args, **kwargs)
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory(dir=TEST_CACHE) as directory:
                with patch.object(Path, 'read_text', mutated), self.assertRaises(ValueError):
                    build(directory)
                self.assertEqual(list(Path(directory).iterdir()), [])

    def test_source_text_is_html_escaped(self):
        source = copy.deepcopy(self.sources[0])
        source['quote'] = '<img src=x onerror=alert(1)>'
        source['author']['name'] = '<script>unsafe</script>'
        rendered = source_note(source)
        self.assertNotIn('<img', rendered)
        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;img', rendered)
        self.assertIn('&lt;script&gt;', rendered)

    def test_public_json_is_allowlisted_metadata_and_short_quotes_only(self):
        for source in self.sources:
            self.assertFalse({'text', 'body', 'plain_text', 'article', 'note_post'} & source.keys())
        for entry in self.coverage['exclusions']:
            self.assertFalse({'text', 'body', 'plain_text', 'article'} & entry.keys())
        # Strict schema validation runs in load(); no unknown body fields can pass.
        load()
        self.assertFalse((ROOT / 'site/search-index.json').exists())
        self.assertFalse((ROOT / 'site/catalog.html').exists())

    def test_available_private_cache_has_no_full_post_or_long_article_in_publication(self):
        # Optional extra audit on the implementation checkout; fresh clones use
        # the synthetic fixture tests and public quote/schema contracts instead.
        files = [p for p in (ROOT / 'site').rglob('*') if p.is_file()]
        files += [p for p in (ROOT / 'data/thedankoe').glob('*.json')]
        files += list((ROOT / 'editorial/thedankoe').glob('*.json'))
        validate_hygiene(ROOT / 'data/thedankoe/raw', files)
        raw = ROOT / 'data/thedankoe/raw/x-api/search-posts-all-02.json'
        if not raw.exists():
            return
        posts = read_json(raw)['response']['data']
        published = [p.read_text() for p in files]
        for post in posts:
            body = post.get('article', {}).get('plain_text')
            if body:
                for text in published:
                    self.assertFalse(matching_passage(body, text))
                    self.assertNotIn(body, text)
            elif post['id'] in {s['post_id'] for s in self.sources} and len(post['text']) > 68:
                for text in published:
                    self.assertNotIn(post['text'], text)
                    self.assertNotIn(json.dumps(post['text'], ensure_ascii=False)[1:-1], text)

    def test_mobile_css_contracts_keep_375px_reading_measure(self):
        css = (ROOT / 'web/reader.css').read_text()
        for expected in ('max-width: 66ch', 'min-width: 0', '@media (max-width: 760px)',
                         '.book { display: block; padding: 1rem; }', '.contents ul { display: flex; flex-wrap: wrap',
                         'overflow-wrap: anywhere', ':focus-visible', 'forced-colors: active',
                         'prefers-reduced-motion: reduce', '@media (max-width: 400px)', '.source-note', 'blockquote'):
            self.assertIn(expected, css)
        self.assertNotRegex(css, r'(?<!max-)\bwidth:\s*(?:[4-9]\d\d|\d{4,})px')
        self.assertNotIn('overflow-x: hidden', css)
        self.assertGreaterEqual(375 - 2 * 8 - 2 * 16 - 2, 320)
        self.assertEqual(css, (ROOT / 'site/assets/reader.css').read_text())
