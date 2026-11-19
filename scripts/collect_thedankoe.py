#!/usr/bin/env python3
"""Serial, bounded, unauthenticated collector. Default invocation is offline.

Raw bodies/state are private local files. Only allowlisted metadata is exported.
Redirects are inspected one hop at a time, with robots checked on every host.
"""
from __future__ import annotations

import argparse
import csv
import io
import hashlib
import json
import math
import re
import time
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.robotparser import RobotFileParser

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = 'FollowBooksResearch/0.1 (small personal research collector; contact: zht7063@users.noreply.github.com)'
BOT = 'FollowBooksResearch'
ALLOWED_HOSTS = {'thedankoe.com', 'www.thedankoe.com', 'letters.thedankoe.com',
                 'eden.so', 'www.eden.so', 'thedankoe.eden.so', 'kortex.co',
                 'www.kortex.co', 'theartoffocusbook.com', 'www.theartoffocusbook.com',
                 'www.youtube.com'}
STATUSES = {'fetched_ok', 'skipped', 'blocked', 'unread', 'unwatched', 'seed_only', 'error'}
MAX_BODY = 5 * 1024 * 1024


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def canonical_url(url):
    parts = urlsplit(url.strip())
    if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password or parts.port:
        raise ValueError('Only credential-free HTTPS URLs without custom ports are accepted')
    return urlunsplit(('https', parts.hostname.lower(), parts.path or '/', parts.query, ''))


def permitted(url):
    try:
        parts = urlsplit(canonical_url(url))
    except ValueError:
        return False
    if parts.hostname not in ALLOWED_HOSTS:
        return False
    if parts.hostname == 'www.youtube.com':
        return parts.path in {'/@DanKoeTalks', '/feeds/videos.xml', '/robots.txt'}
    return True


class PageMetadata(HTMLParser):
    """Extract only metadata; readable text is used locally, never exported."""
    def __init__(self):
        super().__init__()
        self.title = ''
        self.date = None
        self.canonical = None
        self.channel_ids = set()
        self.text = []
        self.hidden = 0
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in {'script', 'style', 'nav', 'footer', 'header', 'form'}:
            self.hidden += 1
        if tag == 'title':
            self.in_title = True
        if tag == 'meta':
            key = a.get('property') or a.get('name') or a.get('itemprop')
            if key in {'article:published_time', 'datePublished', 'date'}:
                match = re.match(r'\d{4}-\d{2}-\d{2}', a.get('content', ''))
                if match:
                    try:
                        datetime.strptime(match[0], '%Y-%m-%d')
                        self.date = {'value': match[0], 'provenance': f'HTML meta {key}'}
                    except ValueError:
                        pass
            if key == 'channelId' and re.fullmatch(r'UC[\w-]{22}', a.get('content', '')):
                self.channel_ids.add(a['content'])
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonical = a.get('href')

    def handle_endtag(self, tag):
        if tag in {'script', 'style', 'nav', 'footer', 'header', 'form'}:
            self.hidden = max(0, self.hidden - 1)
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if not self.hidden and data.strip():
            self.text.append(data.strip())


def restriction(status, body):
    if status in {401, 402, 403, 429, 451}:
        return f'HTTP {status}: access restriction; global crawl stopped'
    lowered = body.lower()
    markers = ('verify you are human', 'cf-chl-', 'g-recaptcha', 'hcaptcha',
               'just a moment...', 'access denied', 'unusual traffic', '<title>captcha', 'captcha required',
               'subscribe to read', 'sign in to continue', 'log in to continue',
               'this post is for paid subscribers', 'automated access is prohibited')
    if any(marker in lowered for marker in markers) or re.search(r'<input[^>]+type=[\"\']?password', lowered):
        return 'Captcha, challenge, login/paywall or explicit access restriction; global crawl stopped'
    return None


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def http_transport(url):
    # No cookie jar, auth handler, browser, session or automatic redirect following.
    opener = build_opener(NoRedirect)
    request = Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'text/html,application/xml,text/plain;q=0.8'})
    try:
        response = opener.open(request, timeout=30)
    except HTTPError as exc:
        response = exc
    with response:
        status, headers = response.code, dict(response.headers)
        # A known restricted status must reach the persistent stop even if its
        # body is huge, stalls, or cannot be decoded. Do not read it at all.
        if restriction(status, ''):
            return status, headers, b''
        chunks, size, tail = [], 0, b''
        while size <= MAX_BODY:
            chunk = response.read(min(65536, MAX_BODY + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
            probe = tail + chunk
            if restriction(status, probe.decode('utf-8', errors='replace')):
                break
            tail = probe[-512:]
        return status, headers, b''.join(chunks)


class Collector:
    def __init__(self, raw_dir, *, transport=http_transport, sleep=time.sleep,
                 clock=time.time, budget=90, delay=10, stale_days=None):
        if not 0 <= budget <= 90 or not math.isfinite(delay) or delay < 8:
            raise ValueError('Budget must be 0–90 and delay must be at least 8 seconds')
        if stale_days is not None and (not math.isfinite(stale_days) or stale_days <= 0):
            raise ValueError('Staleness must be finite and positive')
        self.raw = Path(raw_dir)
        self.raw.mkdir(parents=True, exist_ok=True)
        self.state_path = self.raw / 'state.json'
        self.state = json.loads(self.state_path.read_text()) if self.state_path.exists() else {
            'version': 1, 'responses': {}, 'events': [], 'stop_reason': None,
            'started_at': now(), 'last_request_at': None, 'outcomes': {}}
        self.transport, self.sleep, self.clock = transport, sleep, clock
        self.budget, self.delay, self.stale_days = budget, delay, stale_days
        self.run_attempts = 0
        self.robots = {}
        self.required_delay = self.delay

    def persist(self):
        save_json(self.state_path, self.state)

    def event(self, kind, url, **fields):
        self.state['events'].append({'at': now(), 'kind': kind, 'url': url, **fields})
        self.persist()

    def cached(self, url):
        item = self.state['responses'].get(url)
        if not item:
            return None
        if self.stale_days is not None and self.clock() - item['timestamp'] > self.stale_days * 86400:
            return None
        path = self.raw / item['cache_file'] if item.get('cache_file') else None
        if path and (not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != item['content_hash']):
            self.event('skipped', url, reason='Cache missing or hash mismatch; no implicit re-fetch')
            return {'fetch_status': 'skipped', 'decision_note': 'Cache integrity failure'}
        self.event('cached', url, reason='Persistent completed response reused')
        return item

    def request(self, url, delay=None):
        if self.state['stop_reason']:
            return {'fetch_status': 'blocked', 'decision_note': self.state['stop_reason']}
        cached = self.cached(url)
        if cached:
            return cached
        for attempt in range(3):
            if self.run_attempts >= self.budget:
                self.event('skipped', url, reason='Finite request budget exhausted')
                return {'fetch_status': 'skipped', 'decision_note': 'Request budget exhausted'}
            interval = max(self.required_delay, delay or 0)
            last = self.state['last_request_at']
            if last is not None:
                self.sleep(max(0, interval - (self.clock() - last)))
            self.run_attempts += 1
            self.state['last_request_at'] = self.clock()
            # Persist the attempt before I/O, including interrupted requests in accounting.
            self.event('attempted', url, attempt=attempt + 1)
            try:
                status, headers, body = self.transport(url)
            except (URLError, TimeoutError, OSError):
                self.event('network_error', url, reason='Transient network error (details omitted)')
                if attempt < 2:
                    self.event('backoff', url, seconds=2 ** (attempt + 1), reason='network')
                    self.sleep(2 ** (attempt + 1))
                    continue
                item = {'fetch_status': 'error', 'decision_note': 'Network retry cap reached', 'timestamp': self.clock()}
                self.state['responses'][url] = item
                self.persist()
                return item
            except ValueError:
                self.event('skipped', url, reason='Oversized response')
                return {'fetch_status': 'skipped', 'decision_note': 'Oversized response'}
            text = body.decode('utf-8', errors='replace')
            reason = restriction(status, text)
            if len(body) > MAX_BODY and not reason:
                reason = 'Response exceeds 5 MiB inspection limit; global crawl stopped for manual review'
            digest = hashlib.sha256(body).hexdigest()
            filename = digest + '.body'
            (self.raw / filename).write_bytes(body)
            item = {'fetch_status': 'blocked' if reason else ('fetched_ok' if 200 <= status < 300 else 'error'),
                    'http_status': status, 'content_hash': digest, 'cache_file': filename,
                    'body_truncated': len(body) > MAX_BODY,
                    'timestamp': self.clock(), 'fetched_at': now(), 'decision_note': reason or 'Public HTTP response; no authentication',
                    'location': next((v for k, v in headers.items() if k.lower() == 'location'), None)}
            self.state['responses'][url] = item
            if reason:
                self.state['stop_reason'] = reason
                self.event('blocked', url, http_status=status, reason=reason)
                return item
            self.event('fetched' if 200 <= status < 300 else 'http_error', url, http_status=status)
            if status >= 500 and status <= 599 and attempt < 2:
                self.event('backoff', url, seconds=2 ** (attempt + 1), reason='5xx')
                self.sleep(2 ** (attempt + 1))
                continue
            return item
        raise AssertionError('unreachable')

    def policy(self, url):
        parts = urlsplit(url)
        origin = f'{parts.scheme}://{parts.netloc}'
        if origin in self.robots:
            return self.robots[origin]
        robots_url = origin + '/robots.txt'
        result = self.request(robots_url)
        parser = RobotFileParser()
        if result.get('http_status') in {404, 410}:
            parser.parse([])
        elif result['fetch_status'] == 'fetched_ok':
            body = (self.raw / result['cache_file']).read_text(errors='replace')
            # Conservative interpretation of published machine-use restrictions.
            if re.search(r'(?:ai-input|ai-train|search)\s*=\s*no|noai|noimageai', body, re.I):
                self.state['stop_reason'] = 'Robots content-use restriction; stopped for manual terms review'
                self.event('blocked', robots_url, reason=self.state['stop_reason'])
                return None
            parser.parse(body.splitlines())
        else:
            self.event('skipped', url, reason='Robots unavailable; fail closed')
            return None
        delay = max(self.delay, parser.crawl_delay(BOT) or parser.crawl_delay('*') or 0)
        rate = parser.request_rate(BOT) or parser.request_rate('*')
        if rate and rate.requests:
            delay = max(delay, rate.seconds / rate.requests)
        self.required_delay = max(self.required_delay, delay)
        self.robots[origin] = parser, delay
        return self.robots[origin]

    def fetch(self, url, seen=None):
        url = canonical_url(url)
        if self.state['stop_reason']:
            return {'fetch_status': 'blocked', 'decision_note': 'Retained without request after global stop'}
        if not permitted(url):
            self.event('skipped', url, reason='Outside official-site allowlist / forbidden platform path')
            return {'fetch_status': 'skipped', 'decision_note': 'Outside collection policy'}
        seen = set() if seen is None else seen
        if url in seen or len(seen) >= 5:
            self.event('skipped', url, reason='Redirect cycle or hop limit')
            return {'fetch_status': 'skipped', 'decision_note': 'Redirect cycle or hop limit'}
        seen.add(url)
        policy = self.policy(url)
        if not policy:
            return {'fetch_status': 'blocked' if self.state['stop_reason'] else 'skipped', 'decision_note': self.state['stop_reason'] or 'Robots unavailable'}
        parser, delay = policy
        if not parser.can_fetch(BOT, url):
            self.event('skipped', url, reason='robots.txt disallow')
            return {'fetch_status': 'skipped', 'decision_note': 'robots.txt disallow'}
        result = self.request(url, delay)
        if result.get('http_status') in {301, 302, 303, 307, 308} and result.get('location'):
            target = urljoin(url, result['location'])
            if re.search(r'/(?:login|signin|sign-in|account|auth)(?:/|\?|$)', target, re.I):
                self.state['stop_reason'] = 'Login/account redirect; global crawl stopped without following'
                self.event('blocked', url, reason=self.state['stop_reason'])
                return {**result, 'fetch_status': 'blocked', 'decision_note': self.state['stop_reason']}
            if not permitted(target):
                self.event('skipped', url, reason='Redirect target outside allowlist; not followed')
                return {**result, 'fetch_status': 'skipped', 'decision_note': 'Redirect outside allowlist', 'redirect_to': target}
            redirected = self.fetch(target, seen)
            return {**redirected, 'redirect_from': url, 'final_url': redirected.get('final_url', target)}
        return {**result, 'final_url': url}


def attribution(seed_id, url):
    host = urlsplit(url).hostname
    if host in {'eden.so', 'www.eden.so'}:
        return 'Eden (organization)', 'Company source; individual authorship not verified this run'
    if host in {'kortex.co', 'www.kortex.co'}:
        return 'Kortex (organization)', 'Historical company source; individual authorship not verified this run'
    if seed_id in {'site-08', 'gh-01'}:
        return 'Early @thedankoe account (unverified connection)', 'Seed identity association is uncertain'
    if seed_id.startswith('rec-'):
        return 'Third-party works recommended in the seed', 'Recommendation, not original Dan Koe work'
    return 'Dan Koe', 'Personal source or account, attributed by the seed' + ('; YouTube channel ID unresolved' if seed_id.startswith('yt-') or seed_id == 'site-04' else '')


def seed_sources():
    sources = []
    for row in csv.DictReader(io.StringIO((ROOT / 'original-info/thedankoe/index.csv').read_text())):
        sid = row['id']
        is_x = sid.startswith('x-') or sid == 'site-02' or sid == 'rec-01'
        is_video = sid.startswith('yt-') or sid == 'site-04'
        url = row['X来源链接'] if is_x else row['站外原文或代码链接'] or row['X来源链接']
        status = 'unread' if is_x or '未读全文' in row['核验状态'] or '未逐篇' in row['核验状态'] else 'seed_only'
        if is_video:
            status = 'unwatched'
        section = ('x' if is_x else 'videos' if is_video else 'letters' if sid.startswith('letter-')
                   else 'products' if sid.startswith(('kortex-', 'eden-', 'prod-')) else 'identity')
        author, attribution_note = attribution(sid, url)
        sources.append({'id': sid, 'seed_ids': [sid], 'title': row['标题'], 'url': canonical_url(url),
                        'canonical_url': canonical_url(url), 'date': row['日期'] or None,
                        'date_provenance': {'kind': 'seed', 'seed_id': sid, 'field': '日期', 'note': row['日期说明']} if row['日期'] else None,
                        'author': author, 'attribution_note': attribution_note, 'seed_attribution': row['作者或身份'], 'source_type': row['类型'],
                        'tags': row['主题标签'].split(','), 'section': section,
                        'seed_abstract': None if is_x else row['摘要'], 'seed_verification': row['核验状态'],
                        'fetch_status': status, 'read_status': 'unwatched' if is_video else 'unread' if is_x or status == 'unread' else 'seed_abstract_only',
                        'http_status': None, 'content_hash': None, 'fetched_at': None,
                        'robots_note': 'Not requested this run',
                        'decision_note': 'X URL-only; no re-fetch' if is_x else 'Seed metadata; not read this run'})
    return sources


def collection_plan(sources):
    # Explicit bounded list, not a recursive crawler; no X, GitHub or watch URLs.
    priorities = ['site-01', 'site-03', 'letter-04', 'letter-02', 'letter-12', 'letter-09',
                  'letter-10', 'letter-11', 'letter-01', 'letter-03', 'letter-05',
                  'letter-06', 'letter-07', 'letter-08', 'site-05', 'eden-01',
                  'eden-02', 'eden-03', 'site-07', 'kortex-06', 'kortex-01', 'site-04']
    by_id = {s['id']: s for s in sources}
    return list(dict.fromkeys([by_id[i]['url'] for i in priorities[:1]] +
        ['https://thedankoe.com/sitemap_index.xml', 'https://letters.thedankoe.com/feed',
         'https://letters.thedankoe.com/sitemap.xml'] + [by_id[i]['url'] for i in priorities[1:]]))


def export(collector, sources, outcomes):
    for source in sources:
        outcome = outcomes.get(source['url'])
        if outcome is None:
            # Resume exports from previously completed bodies, without claiming another request.
            outcome = collector.state.get('outcomes', {}).get(source['url']) or collector.state['responses'].get(source['url'])
        if not outcome or source['section'] == 'x':
            if source['section'] == 'x':
                source['decision_note'] = 'X URL-only, unread; collection forbidden and not attempted'
            elif source['section'] == 'videos':
                source['decision_note'] = 'Unwatched; metadata verification not reached before global stop' if collector.state['stop_reason'] else 'Unwatched; no video collection planned'
            else:
                source['decision_note'] = 'Not requested: global crawl stopped before this URL or URL outside finite plan' if collector.state['stop_reason'] else 'Not requested: outside finite plan'
            continue
        for field in ('fetch_status', 'http_status', 'content_hash', 'fetched_at', 'decision_note'):
            if field in outcome:
                source[field] = outcome[field]
        source['robots_note'] = 'robots checked before network request; see request ledger' if outcome.get('http_status') else outcome['decision_note']
        source['canonical_url'] = outcome.get('final_url', source['url'])
        if outcome['fetch_status'] == 'fetched_ok':
            page = PageMetadata()
            page.feed((collector.raw / outcome['cache_file']).read_text(errors='replace'))
            source['observed_title'] = page.title.strip()[:300] or None
            source['observed_date'] = page.date
            source['read_status'] = 'unwatched' if source['section'] == 'videos' else 'fetched_not_reviewed'
            if page.channel_ids:
                source['observed_channel_ids'] = sorted(page.channel_ids)
    reviews_path = ROOT / 'editorial/thedankoe/reviewed-sources.json'
    reviews = json.loads(reviews_path.read_text()) if reviews_path.exists() else {}
    for source in sources:
        review = reviews.get(source['id'])
        if review and source['fetch_status'] == 'fetched_ok' and source['content_hash'] == review['content_hash']:
            source['read_status'] = review['read_status']
            source['review_note'] = review['note']
    events = collector.state['events']
    kinds = Counter(e['kind'] for e in events)
    summary = {'generated_at': now(), 'seed_entries': len(sources), 'request_cap_per_invocation': collector.budget,
               'delay_seconds': collector.delay, 'concurrency': 1, 'user_agent': USER_AGENT,
               'planned_urls': len(collection_plan(sources)), 'new_entries_added': 0,
               'counts': {'attempted': kinds['attempted'], 'fetched': kinds['fetched'], 'cached_hits': kinds['cached'],
                          'skipped': kinds['skipped'], 'blocked': kinds['blocked'], 'network_errors': kinds['network_error'],
                          'unread_retained': sum(s['read_status'] not in {'public_page_reviewed', 'public_excerpt_reviewed'} for s in sources),
                          'sources_reviewed': sum(s['read_status'] in {'public_page_reviewed', 'public_excerpt_reviewed'} for s in sources),
                          'full_public_pages_reviewed': sum(s['read_status'] == 'public_page_reviewed' for s in sources),
                          'sources_fetched_ok': sum(s['fetch_status'] == 'fetched_ok' for s in sources),
                          'sources_not_requested': sum(s['http_status'] is None for s in sources),
                          'x_url_only_retained': sum(s['section'] == 'x' for s in sources),
                          'video_references_unwatched': sum(s['section'] == 'videos' for s in sources)},
               'count_definitions': 'Cumulative HTTP attempts include robots, redirects and retries; cache hits/skips are ledger events. Unread retained includes fetched-but-unreviewed pages, seed abstracts and unwatched items. Excerpt-reviewed pages are counted separately as reviewed, not fully read. Fetched is not read.',
               'hosts_touched': sorted({urlsplit(e['url']).hostname for e in events if e['kind'] == 'attempted'}),
               'stop_reason': collector.state['stop_reason'], 'started_at': collector.state['started_at'],
               'youtube_verification': {'seed_readme_id': 'UCWXYDYv5STLk-zoxMP2I1Lw', 'seed_csv_id': 'UCswG6FSbgZjbWtdf_hMLaow',
                                        'result': 'Unresolved: crawl stopped on a newsletter restriction before channel/RSS verification; neither candidate is adopted as verified.'}}
    save_json(ROOT / 'data/thedankoe/sources.json', sources)
    save_json(ROOT / 'data/thedankoe/collection-summary.json', summary)
    # Allowlist event fields: no response bodies/headers/cookies are published.
    save_json(ROOT / 'data/thedankoe/request-ledger.json', events)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--live', action='store_true', help='Explicitly permit bounded public HTTP requests')
    mode.add_argument('--export-only', action='store_true', help='Offline: re-export existing local state and review notes; no requests')
    parser.add_argument('--budget', type=int, default=90)
    parser.add_argument('--delay', type=float, default=10)
    parser.add_argument('--stale-after-days', type=float, default=None, help='Explicitly refresh completed entries older than this age')
    args = parser.parse_args()
    if args.stale_after_days is not None and (not math.isfinite(args.stale_after_days) or args.stale_after_days <= 0):
        parser.error('stale age must be positive')
    sources = seed_sources()
    if args.export_only:
        raw = ROOT / 'data/thedankoe/raw'
        if not (raw / 'state.json').exists():
            parser.error('No local crawl state exists to export')
        collector = Collector(raw, budget=args.budget, delay=args.delay)
        print(json.dumps(export(collector, sources, collector.state.get('outcomes', {}))['counts']))
        return
    if not args.live:
        print(json.dumps({'mode': 'offline plan; no network or output changes', 'request_cap': args.budget,
                          'urls': collection_plan(sources)}, indent=2))
        return
    collector = Collector(ROOT / 'data/thedankoe/raw', budget=args.budget, delay=args.delay, stale_days=args.stale_after_days)
    outcomes = {}
    try:
        for url in collection_plan(sources):
            if collector.state['stop_reason']:
                break
            outcomes[url] = collector.fetch(url)
            collector.state.setdefault('outcomes', {})[url] = outcomes[url]
            collector.persist()
            # Persist clean progress after every logical source, including a global stop.
            export(collector, sources, outcomes)
            print(json.dumps({'url': url, 'status': outcomes[url]['fetch_status'], 'attempted_this_invocation': collector.run_attempts}), flush=True)
    finally:
        collector.persist()
        print(json.dumps(export(collector, sources, outcomes)['counts']), flush=True)


if __name__ == '__main__':
    main()
