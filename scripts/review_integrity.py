"""Shared hash and review-boundary checks for every publication entry point."""
import json

REVIEW_STATUSES = {'public_page_reviewed', 'public_excerpt_reviewed'}


def load_reviews(root):
    # A missing registry must not silently preserve metadata review claims.
    return json.loads((root / 'editorial/thedankoe/reviewed-sources.json').read_text())


def matching_review(source, reviews):
    review = reviews.get(source['id'])
    return review if (review and source['fetch_status'] == 'fetched_ok'
                      and source.get('content_hash') == review['content_hash']) else None


def validate_review(source, reviews):
    if source['read_status'] in REVIEW_STATUSES or source.get('review_note'):
        review = matching_review(source, reviews)
        assert review, f'Review registry/hash mismatch: {source["id"]}'
        assert source['read_status'] == review['read_status'], f'Review extent mismatch: {source["id"]}'
        assert source.get('review_note') == review['note'], f'Review note mismatch: {source["id"]}'


def apply_reviews(sources, reviews):
    for source in sources:
        validate_review(source, reviews)
        review = matching_review(source, reviews)
        if review:
            assert review['read_status'] in REVIEW_STATUSES, 'Invalid registry review status'
            source['read_status'] = review['read_status']
            source['review_note'] = review['note']


def withhold_blocked_notes(source):
    if source['fetch_status'] == 'blocked':
        source['seed_abstract'] = None
        source['seed_verification'] = None
        source['read_status'] = 'unread'
        source.pop('review_note', None)
