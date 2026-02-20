"""
AI Personalization service — GPT-4.1 analyzes a user's review history
and bookmarks, then generates a search query used by the existing
weighted-vibe search pipeline to return personalized recommendations.
"""
import json
import logging
import os

import openai

from ..models import Bookmark, Business, Review

logger = logging.getLogger('api')

MODEL = 'gpt-4.1'


def _summarize_business(biz: Business, extra: str = '') -> dict:
    """Build a compact dict of business attributes for the GPT prompt."""
    tags = list(biz.tags.values_list('name', flat=True))
    summary = {
        'name': biz.name,
        'category': biz.category.name if biz.category else None,
        'tags': tags[:15],  # cap to keep prompt small
        'price_level': biz.price_level,
        'avg_rating': float(biz.avg_rating) if biz.avg_rating else None,
    }
    if biz.description:
        summary['description'] = biz.description[:120]
    if extra:
        summary['context'] = extra
    return summary


def gather_user_profile(user) -> list[dict]:
    """
    Collect up to 20 recently-reviewed + 20 bookmarked businesses and
    return compact summaries for the GPT prompt.
    """
    # ── Recent reviews (most recent first) ────────────────────────────────
    recent_reviews = (
        Review.objects
        .filter(user=user)
        .select_related('business', 'business__category')
        .prefetch_related('business__tags')
        .order_by('-created_at')[:20]
    )

    reviewed_items = []
    reviewed_biz_ids = set()
    for r in recent_reviews:
        reviewed_biz_ids.add(r.business_id)
        ctx = f"user rated {r.rating}/5"
        if r.description:
            ctx += f"; said: \"{r.description[:100]}\""
        reviewed_items.append(_summarize_business(r.business, extra=ctx))

    # ── Bookmarks (most recent first, exclude already-reviewed) ──────────
    bookmarks = (
        Bookmark.objects
        .filter(user=user)
        .exclude(business_id__in=reviewed_biz_ids)
        .select_related('business', 'business__category')
        .prefetch_related('business__tags')
        .order_by('-created_at')[:20]
    )
    bookmarked_items = []
    for bk in bookmarks:
        ctx = 'bookmarked'
        if bk.note:
            ctx += f"; note: \"{bk.note[:80]}\""
        bookmarked_items.append(_summarize_business(bk.business, extra=ctx))

    return reviewed_items + bookmarked_items


def generate_search_query(profile_items: list[dict]) -> str:
    """
    Send the user's profile to GPT-4.1 and get back a short, natural-language
    search query that captures their tastes.  This query is then fed directly
    into the existing weighted-vibe search endpoint.
    """
    if not profile_items:
        return 'popular highly rated local businesses'

    client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    system_prompt = (
        "You are a local-business recommendation engine.  The user's recently "
        "reviewed and bookmarked businesses are provided as JSON.  Analyze the "
        "patterns — categories, tags, price range, vibes — and produce a single "
        "SHORT search query (3-8 words) that would find NEW businesses matching "
        "their taste.\n\n"
        "Rules:\n"
        "- Output ONLY the search query, nothing else.\n"
        "- Focus on the dominant themes: cuisine type, vibe, price, experience.\n"
        "- Combine the top 2-3 strongest patterns into one concise query.\n"
        "- Do NOT name specific businesses.\n"
        "- Do NOT add explanations.\n\n"
        "Example outputs:\n"
        "  cozy affordable brunch cafes\n"
        "  trendy cocktail bars live music\n"
        "  family friendly outdoor dining\n"
        "  artisan coffee shops quiet workspace"
    )

    user_content = json.dumps(profile_items, default=str)

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.7,
        max_tokens=60,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_content},
        ],
    )

    query = response.choices[0].message.content.strip().strip('"\'')
    logger.info('AI personalization query for user: "%s"', query)
    return query
