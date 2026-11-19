import json
import io
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from scripts.collect_thedankoe import Collector, MAX_BODY, canonical_url, permitted, http_transport

TEST_CACHE = Path(__file__).resolve().parents[1] / '.cache/tests'
TEST_CACHE.mkdir(parents=True, exist_ok=True)

HOME = 'https://thedankoe.com/'
ROBOTS = HOME + 'robots.txt'
ARTICLE = HOME + 'letters/example/'


class FixtureTransport:
    def __init__(self, responses):
        self.responses = {url: list(values) for url, values in responses.items()}
        self.calls = []
        self.active = 0
        self.peak = 0
        self.threads = set()

    def __call__(self, url):
        self.active += 1
        self.peak = max(self.peak, self.active)
        self.threads.add(threading.get_ident())
        self.calls.append(url)
        try:
            value = self.responses[url].pop(0)
            if isinstance(value, Exception):
                raise value
            return value
        finally:
            self.active -= 1


def response(body='fixture article', status=200, **headers):
    return status, headers, body.encode()


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=TEST_CACHE)
        self.addCleanup(self.directory.cleanup)
        self.sleeps = []
        self.time = 1000

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.time += seconds

    def collector(self, responses, **kwargs):
        transport = FixtureTransport(responses)
        collector = Collector(self.directory.name, transport=transport, sleep=self.sleep, clock=lambda: self.time, **kwargs)
        return collector, transport

    def test_serial_cache_dedup_and_incremental_resume(self):
        c, t = self.collector({ROBOTS: [response('User-agent: *\nAllow: /')], ARTICLE: [response()]})
        result = [c.fetch(ARTICLE), c.fetch(ARTICLE + '#fragment')]
        self.assertEqual(t.calls, [ROBOTS, ARTICLE])
        self.assertEqual(t.peak, 1)
        self.assertEqual(len(t.threads), 1)
        self.assertEqual(result[0]['content_hash'], result[1]['content_hash'])
        resumed, resumed_transport = self.collector({})
        self.assertEqual(resumed.fetch(ARTICLE)['fetch_status'], 'fetched_ok')
        self.assertEqual(resumed_transport.calls, [])
        self.assertTrue(any(e['kind'] == 'cached' for e in resumed.state['events']))
        self.assertTrue(all(seconds >= 10 for seconds in self.sleeps))

    def test_immediate_global_persistent_stop_for_restrictions(self):
        cases = [(429, 'slow down'), (403, 'forbidden'), (401, 'auth'), (451, 'restricted'),
                 (200, '<title>Captcha required</title>'), (200, 'Verify you are human'),
                 (200, 'cf-chl-challenge'), (200, 'Subscribe to read'), (200, 'Sign in to continue')]
        for status, body in cases:
            with self.subTest(status=status, body=body), tempfile.TemporaryDirectory(dir=TEST_CACHE) as directory:
                t = FixtureTransport({ROBOTS: [response('User-agent: *\nAllow: /')], ARTICLE: [response(body, status)]})
                c = Collector(directory, transport=t, sleep=self.sleep, clock=lambda: self.time)
                self.assertEqual(c.fetch(ARTICLE)['fetch_status'], 'blocked')
                before = list(t.calls)
                c.fetch('https://eden.so/')
                resumed = Collector(directory, transport=t, sleep=self.sleep, clock=lambda: self.time)
                resumed.fetch(ARTICLE)
                self.assertEqual(t.calls, before)
                self.assertFalse(any(e['kind'] == 'backoff' for e in c.state['events']))
                self.assertTrue(json.loads((Path(directory) / 'state.json').read_text())['stop_reason'])

    def test_blocked_robots_stops_before_page(self):
        c, t = self.collector({ROBOTS: [response('Forbidden', 403)]})
        self.assertEqual(c.fetch(ARTICLE)['fetch_status'], 'blocked')
        self.assertEqual(t.calls, [ROBOTS])

    def test_robots_disallow_skips_and_crawl_delay_is_honored(self):
        c, t = self.collector({ROBOTS: [response('User-agent: *\nDisallow: /private\nCrawl-delay: 17')], ARTICLE: [response()]})
        self.assertEqual(c.fetch(HOME + 'private')['fetch_status'], 'skipped')
        self.assertEqual(c.fetch(ARTICLE)['fetch_status'], 'fetched_ok')
        self.assertEqual(t.calls, [ROBOTS, ARTICLE])
        self.assertEqual(self.sleeps, [17])
        self.assertTrue(any(e.get('reason') == 'robots.txt disallow' for e in c.state['events']))

    def test_robots_terms_fail_closed(self):
        c, t = self.collector({ROBOTS: [response('User-agent: *\nContent-Signal: ai-input=no')]})
        self.assertEqual(c.fetch(ARTICLE)['fetch_status'], 'blocked')
        self.assertEqual(t.calls, [ROBOTS])

    def test_network_and_5xx_only_have_finite_backoff(self):
        c, t = self.collector({ROBOTS: [response('User-agent: *\nAllow: /')], ARTICLE: [URLError('transient'), response('server', 503), response()]})
        self.assertEqual(c.fetch(ARTICLE)['fetch_status'], 'fetched_ok')
        self.assertEqual(t.calls.count(ARTICLE), 3)
        self.assertEqual([e['seconds'] for e in c.state['events'] if e['kind'] == 'backoff'], [2, 4])
        other = HOME + 'missing'
        t.responses[other] = [response('missing', 404)]
        self.assertEqual(c.fetch(other)['fetch_status'], 'error')
        self.assertEqual(t.calls.count(other), 1)

    def test_retry_cap_and_budget_include_robots_and_retries(self):
        c, t = self.collector({ROBOTS: [response('', 404)], ARTICLE: [response('server', 500)] * 3}, budget=3)
        self.assertEqual(c.fetch(ARTICLE)['fetch_status'], 'skipped')
        self.assertEqual(len(t.calls), 3)
        self.assertEqual(c.run_attempts, 3)

    def test_redirects_recheck_robots_and_forbidden_hosts_are_never_requested(self):
        c, t = self.collector({ROBOTS: [response('User-agent: *\nAllow: /')], ARTICLE: [response('', 302, Location='https://eden.so/')],
                               'https://eden.so/robots.txt': [response('User-agent: *\nDisallow: /')]})
        self.assertEqual(c.fetch(ARTICLE)['fetch_status'], 'skipped')
        self.assertNotIn('https://eden.so/', t.calls)
        before = list(t.calls)
        self.assertEqual(c.fetch('https://x.com/thedankoe')['fetch_status'], 'skipped')
        self.assertEqual(c.fetch('https://www.youtube.com/watch?v=anything')['fetch_status'], 'skipped')
        self.assertEqual(t.calls, before)

    def test_redirect_to_login_restriction_stops_globally(self):
        c, t = self.collector({ROBOTS: [response('User-agent: *\nAllow: /')], ARTICLE: [response('', 302, Location='/login')], HOME + 'login': [response('Sign in to continue')]})
        self.assertEqual(c.fetch(ARTICLE)['fetch_status'], 'blocked')
        c.fetch('https://eden.so/')
        self.assertEqual(t.calls, [ROBOTS, ARTICLE])

    def test_cache_corruption_does_not_implicitly_refetch(self):
        c, t = self.collector({ROBOTS: [response('', 404)], ARTICLE: [response()]})
        result = c.fetch(ARTICLE)
        (Path(self.directory.name) / result['cache_file']).write_text('tampered')
        self.assertEqual(c.fetch(ARTICLE)['fetch_status'], 'skipped')
        self.assertEqual(t.calls, [ROBOTS, ARTICLE])

    def test_explicit_staleness_can_refresh_completed_urls(self):
        c, t = self.collector({ROBOTS: [response('', 404)], ARTICLE: [response('old')]})
        c.fetch(ARTICLE)
        self.time += 2 * 86400
        resumed, t = self.collector({ROBOTS: [response('', 404)], ARTICLE: [response('new')]}, stale_days=1)
        self.assertEqual(resumed.fetch(ARTICLE)['fetch_status'], 'fetched_ok')
        self.assertEqual(t.calls, [ROBOTS, ARTICLE])

    def test_oversized_restrictions_stop_before_size_limit_skip(self):
        for status, prefix in [(403, ''), (429, ''), (200, 'Verify you are human')]:
            with self.subTest(status=status), tempfile.TemporaryDirectory(dir=TEST_CACHE) as directory:
                t = FixtureTransport({ROBOTS: [response('', 404)], ARTICLE: [response(prefix + 'a' * (MAX_BODY + 1), status)]})
                c = Collector(directory, transport=t, sleep=self.sleep, clock=lambda: self.time)
                self.assertEqual(c.fetch(ARTICLE)['fetch_status'], 'blocked')
                c.fetch('https://eden.so/')
                self.assertEqual(t.calls, [ROBOTS, ARTICLE])
                self.assertTrue(c.state['stop_reason'])

    def test_http_adapter_handles_restriction_before_body_errors(self):
        class FakeResponse:
            def __init__(self, status, body, fail_after_first=False):
                self.code, self.headers = status, {}
                self.stream = io.BytesIO(body)
                self.reads = 0
                self.fail_after_first = fail_after_first
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, limit):
                self.reads += 1
                if self.code in {403, 429} or self.fail_after_first and self.reads > 1:
                    raise TimeoutError('Fixture: restricted body must not be read further')
                return self.stream.read(limit)
        for status in [403, 429]:
            remote = FakeResponse(status, b'x' * (MAX_BODY + 1))
            with patch('scripts.collect_thedankoe.build_opener') as opener:
                opener.return_value.open.return_value = remote
                actual, _, body = http_transport(ARTICLE)
            self.assertEqual(actual, status)
            self.assertEqual(remote.reads, 0)
            self.assertEqual(body, b'')
        remote = FakeResponse(200, b'Verify you are human' + b'x' * 65536, fail_after_first=True)
        with patch('scripts.collect_thedankoe.build_opener') as opener:
            opener.return_value.open.return_value = remote
            actual, _, body = http_transport(ARTICLE)
        self.assertEqual(remote.reads, 1)
        self.assertIn(b'Verify you are human', body)
        remote = FakeResponse(200, b'x' * (MAX_BODY + 100))
        with patch('scripts.collect_thedankoe.build_opener') as opener:
            opener.return_value.open.return_value = remote
            _, _, body = http_transport(ARTICLE)
        self.assertEqual(len(body), MAX_BODY + 1)

    def test_nonfinite_delays_and_staleness_are_rejected(self):
        for value in [float('nan'), float('inf'), float('-inf')]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Collector(self.directory.name, delay=value)
                with self.assertRaises(ValueError):
                    Collector(self.directory.name, stale_days=value)

    def test_url_and_configuration_policy(self):
        self.assertEqual(canonical_url('https://TheDanKoe.com#top'), HOME)
        for url in ['http://thedankoe.com/', 'https://user:pass@thedankoe.com/', 'https://thedankoe.com:443/', 'https://localhost/', 'https://thedankoe.com.evil.test/']:
            self.assertFalse(permitted(url))
        with self.assertRaises(ValueError):
            Collector(self.directory.name, budget=91)
        with self.assertRaises(ValueError):
            Collector(self.directory.name, delay=7)
