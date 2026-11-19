#!/usr/bin/env python3
"""Import the fixed five-post sample from three private files, entirely offline.

Only allowlisted metadata and bounded quotations cross the publication boundary.
The private selected manifest is cross-checked against the official response;
its completeness label alone is never sufficient.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/thedankoe/raw/x-api'
PUBLIC = ROOT / 'data/thedankoe'
AUTHOR = {'name': 'DAN KOE', 'username': 'thedankoe', 'id': '256523056'}
QUERY = 'from:thedankoe -is:retweet -is:reply'
# Editorial quote choices, in thematic reading order. No unseen text is supplied.
SELECTION = (
    ('2121636177702727868', "You don't need experience to start, you gain experience by starting."),
    ('2118387157794496581', 'You have to reach the point where your fear of dying mediocre outweighs your fear of looking like an idiot.'),
    ('2122717500014022904', "You can't improve what doesn't exist, and your first version will suck."),
    ('2119463899774767513', 'You have nothing better to do than to work on something meaningful.'),
    ('2116156997712195646', 'Your competition was non existent to begin with, and your only real competition is your own mind.'),
)
EXCLUSIONS = (
    ('2116921689426583713', 'truncated_preview', '预览在句中截断；不补写缺失文字。'),
    ('2114027336421032268', 'truncated_preview', '预览在句中截断；不补写缺失文字。'),
    ('2122374187935523045', 'unfetched_link', '附带链接目标未取得；不推断链接内容。'),
    ('2117664712532123680', 'long_article', '长 X 文章，不转载，也不作为样章正文。'),
    ('2112586533610156368', 'long_article', '长 X 文章，不转载，也不作为样章正文。'),
)
CONVERSATION_NOTE = '独立短帖；conversation_id 等于 post_id。未作为串文或长文，也不声称读取了回复。'
COMPLETENESS_NOTE = 'display_text_range 覆盖全部已取得文字，且末尾为完整句子；仅指这条短帖完整。'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def singapore_time(value):
    require(isinstance(value, str) and value.endswith('Z'), 'created_at must be an official UTC timestamp')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(parsed.utcoffset() == timezone.utc.utcoffset(parsed), 'created_at must be UTC')
    return parsed.astimezone(ZoneInfo('Asia/Singapore')).strftime('%Y-%m-%d %H:%M:%S +08 (Asia/Singapore)')


def post_url(post_id):
    return f'https://x.com/thedankoe/status/{post_id}'


def validate_sources(sources):
    """Validate the public format without requiring any private cache."""
    require(len(sources) == 5, 'Exactly five sources required')
    keys = {'id', 'post_id', 'url', 'author', 'created_at', 'created_at_singapore', 'lang',
            'fetched_text_length', 'display_text_range', 'completeness', 'completeness_note',
            'conversation_id', 'conversation_completeness_note', 'content_hash', 'provenance', 'quote'}
    for number, (source, (post_id, quote)) in enumerate(zip(sources, SELECTION), 1):
        require(set(source) == keys, 'Unexpected/missing public source field')
        require(source['id'] == f'x-sample-{number:02}' and source['post_id'] == post_id, 'Wrong sample order or post id')
        require(source['url'] == post_url(post_id) and source['author'] == AUTHOR, 'Wrong attribution or URL')
        require(source['created_at_singapore'] == singapore_time(source['created_at']), 'Invented Singapore date')
        require(source['lang'] == 'en', 'Unexpected language')
        length = source['fetched_text_length']
        require(type(length) is int and 0 < length <= 300, 'Not a short post')
        require(source['display_text_range'] == [0, length], 'Incomplete display range')
        require(source['completeness'] == 'complete_short_post', 'Incomplete post')
        require(source['completeness_note'] == COMPLETENESS_NOTE, 'Missing completeness evidence')
        require(source['conversation_id'] == post_id and source['conversation_completeness_note'] == CONVERSATION_NOTE,
                'Not a standalone short post')
        digest = source['content_hash']
        require(set(digest) == {'algorithm', 'value', 'scope'} and digest['algorithm'] == 'sha256'
                and len(digest['value']) == 64 and all(c in '0123456789abcdef' for c in digest['value'])
                and digest['scope'] == 'UTF-8 bytes of official fetched text, unchanged', 'Invalid content hash')
        require(source['quote'] == quote and len(quote) <= 120 and len(quote.split()) <= 25, 'Quote exceeds fixed short selection')
        require(len(quote) < length or (post_id == SELECTION[0][0] and length == 68), 'Whole-post quotation disallowed')
        provenance = source['provenance']
        require(set(provenance) == {'tool', 'namespace', 'query', 'max_results', 'queried_at', 'response_file',
                                    'selection_file', 'date_field', 'author_field'}, 'Unexpected provenance fields')
        require(provenance['tool'] == 'x.search_posts_all' and provenance['namespace'] == 'x'
                and provenance['query'] == QUERY and provenance['max_results'] == 10, 'Wrong official provenance')
        require(provenance['response_file'] == 'search-posts-all-02.json'
                and provenance['selection_file'] == 'selected-sample-posts.json'
                and provenance['date_field'] == 'created_at (UTC)'
                and provenance['author_field'] == 'author_id + includes.users', 'Missing provenance')
        require(datetime.fromisoformat(provenance['queried_at']).utcoffset() is not None, 'Missing query timezone')


def validate_coverage(coverage, sources):
    require(set(coverage) == {'scope', 'official_result_count', 'selected_count', 'selected_ids', 'selection_order',
                             'initial_search', 'corrective_search', 'exclusions', 'outside_sample', 'user_gate'},
            'Unexpected/missing coverage fields')
    require(coverage['scope'] == 'small_unofficial_sample' and coverage['official_result_count'] == 10
            and coverage['selected_count'] == 5, 'Wrong coverage counts')
    require(coverage['selected_ids'] == [s['id'] for s in sources]
            and coverage['selection_order'] == 'thematic_not_chronological', 'Wrong coverage selection')
    first = coverage['initial_search']
    require(first == {'response_file': 'search-posts-all-01.json', 'result_count': 0,
                     'outcome': 'success_empty', 'restriction': False}, 'Empty search was not a restriction')
    require(coverage['corrective_search'] == {**sources[0]['provenance'], 'result_count': 10}, 'Wrong search provenance')
    require(len(coverage['exclusions']) == 5, 'Missing exclusions')
    for entry, (post_id, reason, note) in zip(coverage['exclusions'], EXCLUSIONS):
        keys = {'post_id', 'url', 'reason', 'note'} | ({'title', 'plain_len'} if reason == 'long_article' else set())
        require(set(entry) == keys and entry['post_id'] == post_id and entry['url'] == post_url(post_id)
                and entry['reason'] == reason and entry['note'] == note, 'Wrong exclusion metadata')
    articles = coverage['exclusions'][-2:]
    require([(a['title'], a['plain_len']) for a in articles] == [
        ('The most lucrative AI business to start in 2027', 20156),
        ('The influencer is dead. The Age of Experience is here.', 16373)], 'Wrong article metadata')
    require(coverage['outside_sample'] == '旧 63 条种子目录、旧人物介绍与来源索引均非本样章素材；未取得或未读条目不作内容概括。'
            and coverage['user_gate'] == '交付此小样后停止，等待用户审阅；不扩充来源。', 'Missing scope boundary')


def normalize(raw_dir=RAW):
    raw_dir = Path(raw_dir)
    first = read_json(raw_dir / 'search-posts-all-01.json')
    search = read_json(raw_dir / 'search-posts-all-02.json')
    selection = read_json(raw_dir / 'selected-sample-posts.json')
    require(first['tool'] == 'x.search_posts_all' and first['namespace'] == 'x'
            and first['result']['meta']['result_count'] == 0
            and first['http_outcome'] == 'success_empty' and first['restriction'] is False, 'Unexpected first-search outcome')
    require(search['tool'] == 'x.search_posts_all' and search['namespace'] == 'x'
            and search['query'] == QUERY and search['max_results'] == 10, 'Unexpected search')
    response = search['response']
    posts = {p['id']: p for p in response['data']}
    require(response['meta']['result_count'] == len(response['data']) == len(posts) == 10, 'Expected ten unique results')
    require(set(posts) == {p for p, _ in SELECTION} | {p for p, _, _ in EXCLUSIONS}, 'Unexpected corpus')
    user = next(u for u in response['includes']['users'] if u['id'] == AUTHOR['id'])
    require({k: user[k] for k in AUTHOR} == AUTHOR, 'Unexpected official author')
    require(all(p['author_id'] == AUTHOR['id'] for p in posts.values()), 'Mixed authors')
    selected = selection['selected_for_sample']
    require([p['post_id'] for p in selected] == [p for p, _ in SELECTION], 'Wrong selected posts/order')
    provenance = {'tool': search['tool'], 'namespace': search['namespace'], 'query': search['query'],
                  'max_results': search['max_results'], 'queried_at': search['queried_at'],
                  'response_file': 'search-posts-all-02.json', 'selection_file': 'selected-sample-posts.json',
                  'date_field': 'created_at (UTC)', 'author_field': 'author_id + includes.users'}
    sources = []
    for number, (saved, (post_id, quote)) in enumerate(zip(selected, SELECTION), 1):
        post = posts[post_id]
        text = post['text']  # Private only: never copied into a public record.
        for field in ('text', 'created_at', 'lang', 'author_id', 'conversation_id', 'display_text_range', 'url'):
            require(saved[field] == post[field], f'Selection disagrees with response: {post_id}/{field}')
        require(saved['sample_id'] == f'x-sample-{number:02}' and saved['author_name'] == AUTHOR['name']
                and saved['author_username'] == AUTHOR['username'], 'Wrong selected attribution')
        require(not post.get('article') and not post.get('note_tweet') and not post.get('note_post')
                and not saved.get('note_post') and saved['has_article'] is False, 'Longform is excluded')
        require(saved['completeness'] == 'complete_short_post' and saved['same_as_conversation'] is True
                and post['conversation_id'] == post_id and post['display_text_range'] == [0, len(text)]
                and text.rstrip().endswith(('.', '!', '?')), 'Incomplete or non-standalone post')
        digest = hashlib.sha256(text.encode('utf-8')).hexdigest()
        require(saved['text_sha256'] == digest and saved['fetched_text_length'] == len(text), 'Hash or length mismatch')
        display_time = singapore_time(post['created_at'])
        require(saved['created_at_singapore'] == display_time, 'Selected date mismatch')
        require(quote in text, 'Quote absent from official text')
        sources.append({'id': saved['sample_id'], 'post_id': post_id, 'url': post['url'], 'author': dict(AUTHOR),
                        'created_at': post['created_at'], 'created_at_singapore': display_time, 'lang': post['lang'],
                        'fetched_text_length': len(text), 'display_text_range': post['display_text_range'],
                        'completeness': saved['completeness'], 'completeness_note': COMPLETENESS_NOTE,
                        'conversation_id': post['conversation_id'], 'conversation_completeness_note': CONVERSATION_NOTE,
                        'content_hash': {'algorithm': 'sha256', 'value': digest,
                                         'scope': 'UTF-8 bytes of official fetched text, unchanged'},
                        'provenance': dict(provenance), 'quote': quote})
    exclusions = []
    for post_id, reason, note in EXCLUSIONS:
        post = posts[post_id]
        entry = {'post_id': post_id, 'url': post_url(post_id), 'reason': reason, 'note': note}
        if reason == 'truncated_preview':
            require(not post['text'].rstrip().endswith(('.', '!', '?')), 'Truncation evidence changed')
        elif reason == 'unfetched_link':
            require(post['display_text_range'][1] < len(post['text']) and post.get('entities', {}).get('urls'),
                    'Link exclusion evidence changed')
        else:
            article = post['article']
            entry.update(title=article['title'], plain_len=len(article['plain_text']))
        exclusions.append(entry)
    coverage = {'scope': 'small_unofficial_sample', 'official_result_count': 10, 'selected_count': 5,
                'selected_ids': [s['id'] for s in sources], 'selection_order': 'thematic_not_chronological',
                'initial_search': {'response_file': 'search-posts-all-01.json', 'result_count': 0,
                                   'outcome': 'success_empty', 'restriction': False},
                'corrective_search': {**provenance, 'result_count': 10}, 'exclusions': exclusions,
                'outside_sample': '旧 63 条种子目录、旧人物介绍与来源索引均非本样章素材；未取得或未读条目不作内容概括。',
                'user_gate': '交付此小样后停止，等待用户审阅；不扩充来源。'}
    validate_sources(sources)
    validate_coverage(coverage, sources)
    return sources, coverage


def write_import(raw_dir=RAW, output_dir=PUBLIC):
    sources, coverage = normalize(raw_dir)  # Validate everything before any write.
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, value in [('sample-sources.json', sources), ('sample-coverage.json', coverage)]:
        (output_dir / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return sources, coverage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', type=Path, default=RAW, help='Local fixture/cache directory; never a URL')
    parser.add_argument('--output-dir', type=Path, default=PUBLIC)
    args = parser.parse_args()
    try:
        write_import(args.raw_dir, args.output_dir)
    except (OSError, ValueError, KeyError, StopIteration, TypeError) as error:
        # Do not print payloads or arbitrary field values from the private response.
        parser.exit(1, f'Offline import failed ({type(error).__name__}); check the three local input files.\n')
    print('Imported 5 complete short posts; recorded 10 official results and 5 exclusions. No network used.')


if __name__ == '__main__':
    main()
