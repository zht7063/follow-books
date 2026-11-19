import json
import hashlib
import io
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from scripts.collect_thedankoe import Collector, MAX_BODY, canonical_url, permitted, http_transport, restriction

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
        cases = [(402, 'payment required'), (429, 'slow down'), (403, 'forbidden'), (401, 'auth'), (451, 'restricted'),
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

    def test_restrictions_do_not_write_bodies_even_when_cache_writes_fail(self):
        for status, body in [(200, 'This post is for paid subscribers'), (403, 'denied'), (429, 'slow')]:
            with self.subTest(status=status), tempfile.TemporaryDirectory(dir=TEST_CACHE) as directory:
                t = FixtureTransport({ARTICLE: [response(body, status)]})
                c = Collector(directory, transport=t, sleep=self.sleep, clock=lambda: self.time)
                with patch.object(Path, 'write_bytes', side_effect=OSError('fixture cache failure')) as write:
                    self.assertEqual(c.request(ARTICLE)['fetch_status'], 'blocked')
                write.assert_not_called()
                state = json.loads(c.state_path.read_text())
                self.assertTrue(state['stop_reason'])
                self.assertEqual(state['responses'][ARTICLE]['fetch_status'], 'blocked')
                self.assertNotIn('cache_file', state['responses'][ARTICLE])
                self.assertEqual(list(Path(directory).glob('*.body')), [])
                resumed = Collector(directory, transport=t, sleep=self.sleep, stale_days=1e-12)
                self.assertEqual(resumed.request('https://eden.so/')['fetch_status'], 'blocked')
                self.assertEqual(resumed.fetch('https://eden.so/')['fetch_status'], 'blocked')
                self.assertEqual(t.calls, [ARTICLE])

    def test_stop_persistence_failure_raises_and_reload_fails_closed(self):
        c, t = self.collector({ARTICLE: [response('Subscribe to read')]})
        persist = c.persist
        def fail_stop():
            if c.state['stop_reason']:
                raise OSError('fixture stop persistence failure')
            persist()
        with patch.object(c, 'persist', side_effect=fail_stop):
            with self.assertRaises(OSError):
                c.request(ARTICLE)
        self.assertTrue(c.state['stop_reason'])
        self.assertEqual(c.request('https://eden.so/')['fetch_status'], 'blocked')
        self.assertIsNone(json.loads(c.state_path.read_text())['stop_reason'])
        resumed, _ = self.collector({})
        self.assertTrue(resumed.state['stop_reason'])
        self.assertEqual(resumed.request('https://eden.so/')['fetch_status'], 'blocked')
        self.assertEqual(t.calls, [ARTICLE])

    def test_policy_stop_persistence_failure_cannot_resume_fresh_or_cached_fetch(self):
        for policy in ['login', 'robots']:
            for cached in [False, True]:
                with self.subTest(policy=policy, cached=cached), tempfile.TemporaryDirectory(dir=TEST_CACHE) as directory:
                    body = 'Content-Signal: ai-input=no' if policy == 'robots' else ''
                    restricted_url = ROBOTS if policy == 'robots' else ARTICLE
                    status = 200 if policy == 'robots' else 302
                    t = FixtureTransport({ROBOTS: [response(body if policy == 'robots' else '', 200 if policy == 'robots' else 404)],
                                          ARTICLE: [response('', 302, Location='/login')]})
                    c = Collector(directory, transport=t, sleep=self.sleep, clock=lambda: self.time)
                    if cached:
                        (c.raw / 'legacy.body').write_text(body)
                        c.state['responses'][restricted_url] = {
                            'fetch_status': 'fetched_ok' if policy == 'robots' else 'error',
                            'http_status': status, 'location': '/login' if policy == 'login' else None,
                            'cache_file': 'legacy.body', 'content_hash': hashlib.sha256(body.encode()).hexdigest(),
                            'timestamp': self.time, 'fetched_at': '2026-11-19T00:00:00+00:00'}
                        c.persist()
                    persist = c.persist
                    def fail_stop():
                        if c.state['stop_reason']:
                            raise OSError('fixture policy stop persistence failure')
                        persist()
                    with patch.object(c, 'persist', side_effect=fail_stop), self.assertRaises(OSError):
                        c.fetch(ARTICLE)
                    calls = list(t.calls)
                    self.assertTrue(c.state['stop_reason'])
                    resumed = Collector(directory, transport=t, sleep=self.sleep, stale_days=1e-12)
                    self.assertTrue(resumed.state['stop_reason'])
                    self.assertEqual(resumed.fetch('https://eden.so/')['fetch_status'], 'blocked')
                    self.assertEqual(t.calls, calls)
                    if not cached:
                        # Restricted login/robots responses never enter the body cache.
                        self.assertNotIn(restricted_url, json.loads(c.state_path.read_text())['responses'])

    def test_load_recovers_missing_stop_from_block_evidence(self):
        for evidence in ['event', 'response', 'attempt', 'fetch']:
            with self.subTest(evidence=evidence):
                c, _ = self.collector({})
                c.state['stop_reason'] = None
                c.state['events'] = [] if evidence == 'response' else [
                    {'kind': 'blocked' if evidence == 'event' else 'fetch_started' if evidence == 'fetch' else 'attempted', 'url': ARTICLE}]
                c.state['responses'] = {ARTICLE: {'fetch_status': 'blocked'}} if evidence == 'response' else {}
                c.persist()
                before = c.state_path.read_bytes()
                resumed, t = self.collector({})
                self.assertTrue(resumed.state['stop_reason'])
                self.assertEqual(resumed.fetch('https://eden.so/')['fetch_status'], 'blocked')
                self.assertEqual(t.calls, [])
                self.assertEqual(c.state_path.read_bytes(), before)

    def test_visible_text_gate_variants_stop_globally(self):
        variants = ['This post is for <strong>paid subscribers</strong>', 'Subscribe&nbsp;to read',
                    'Only paid subscribers can access this post', 'Subscribe&#160;to <em>continue reading</em>',
                    'Sign <b>in</b> to continue', 'This article is for paid subscribers only',
                    'Subscribe&NewLine;to read', 'Subscr&#73;be to read', 'Sub<strong>scribe</strong> to read']
        for body in variants:
            with self.subTest(body=body), tempfile.TemporaryDirectory(dir=TEST_CACHE) as directory:
                t = FixtureTransport({ARTICLE: [response(body)]})
                c = Collector(directory, transport=t, sleep=self.sleep, clock=lambda: self.time)
                self.assertEqual(c.request(ARTICLE)['fetch_status'], 'blocked')
                resumed = Collector(directory, transport=t, sleep=self.sleep)
                self.assertEqual(resumed.fetch('https://eden.so/')['fetch_status'], 'blocked')
                self.assertEqual(t.calls, [ARTICLE])
        self.assertIsNone(restriction(200, '<p>A public article about learning.</p>'))

    def test_uninspectable_transport_value_error_stops_globally(self):
        c, t = self.collector({ARTICLE: [ValueError('Oversized response')]})
        self.assertEqual(c.request(ARTICLE)['fetch_status'], 'blocked')
        resumed, _ = self.collector({})
        self.assertEqual(resumed.fetch('https://eden.so/')['fetch_status'], 'blocked')
        self.assertTrue(json.loads(c.state_path.read_text())['stop_reason'])
        self.assertEqual(t.calls, [ARTICLE])

    def test_restricted_redirect_keeps_blocked_outcome(self):
        c, t = self.collector({ROBOTS: [response('', 404)],
                               ARTICLE: [response('This post is for paid subscribers', 302, Location='https://example.invalid/')]})
        request = c.request
        def classified_response(url, delay=None):
            item = request(url, delay)
            # A blocked response may retain Location metadata (e.g. older cache
            # formats); ordinary redirect handling must never override it.
            return {**item, 'location': 'https://example.invalid/'} if url == ARTICLE else item
        with patch.object(c, 'request', side_effect=classified_response):
            self.assertEqual(c.fetch(ARTICLE)['fetch_status'], 'blocked')
        self.assertTrue(json.loads(c.state_path.read_text())['stop_reason'])
        self.assertEqual(c.fetch('https://eden.so/')['fetch_status'], 'blocked')
        self.assertEqual(t.calls, [ROBOTS, ARTICLE])
        self.assertFalse(any(e['kind'] == 'skipped' for e in c.state['events']))

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
        for status, prefix in [(403, ''), (429, ''), (200, 'Verify you are human'), (200, '')]:
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
        for url, marker in [(ARTICLE, b'Verify you are human'), (ROBOTS, b'Content-Signal: ai-input=no')]:
            remote = FakeResponse(200, marker + b'x' * 65536, fail_after_first=True)
            with patch('scripts.collect_thedankoe.build_opener') as opener:
                opener.return_value.open.return_value = remote
                actual, _, body = http_transport(url)
            self.assertEqual(remote.reads, 1)
            self.assertIn(marker, body)
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
