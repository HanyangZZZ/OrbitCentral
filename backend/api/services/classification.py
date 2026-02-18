"""
AI classification — gpt-4o-mini business classification and tagging.
"""
import json
import logging

from concurrent.futures import ThreadPoolExecutor, as_completed

import openai

from ..models import Category, Tag

logger = logging.getLogger('api')


def _load_category_list() -> tuple[str, dict[str, int]]:
    """
    Build a formatted category list from the DB and a slug→id map.
    Returns (prompt_text, slug_map).
    """
    parents = Category.objects.filter(parent__isnull=True).prefetch_related('children')
    lines = []
    all_valid_names = []
    slug_map: dict[str, int] = {}  # slug → category id
    for p in parents:
        children = list(p.children.all())
        child_names = [c.name for c in children]
        lines.append(f"- {p.name}: {', '.join(child_names)}")
        all_valid_names.append(p.name)
        all_valid_names.extend(child_names)
        slug_map[p.slug] = p.id
        for c in children:
            slug_map[c.slug] = c.id
    lines.append(f"\nVALID NAMES (use exactly one of these): {', '.join(all_valid_names)}")
    return '\n'.join(lines), slug_map


def _load_popular_tags(min_usage: int = 3, limit: int = 120) -> str:
    """Load existing popular tags from DB to encourage AI reuse."""
    from django.db.models import Count
    popular = (
        Tag.objects
        .annotate(usage=Count('businesses'))
        .filter(usage__gte=min_usage)
        .order_by('-usage')
        .values_list('name', flat=True)[:limit]
    )
    return ', '.join(f'"{t}"' for t in popular)


def _ai_classify_and_tag(client: openai.OpenAI, places: list[dict]) -> tuple[list[dict], dict[str, int]]:
    """
    Use gpt-4o-mini to classify businesses as small/independent, assign a
    category, and generate descriptive tags.
    Processes batches of 10 concurrently with 20 workers.
    """
    # Load categories dynamically from DB
    category_prompt, category_slug_map = _load_category_list()

    # Load existing popular tags so the AI reuses them
    existing_tags_str = _load_popular_tags()

    results = []
    batch_size = 10
    batches = [places[i:i + batch_size] for i in range(0, len(places), batch_size)]

    def _classify_batch(batch):
        batch_info = []
        for p in batch:
            batch_info.append({
                'id': p.get('id', ''),
                'name': p.get('displayName', {}).get('text', ''),
                'types': p.get('types', []),
                'primary_type': p.get('primaryType', ''),
                'address': p.get('formattedAddress', ''),
                'description': p.get('editorialSummary', {}).get('text', ''),
                'rating': p.get('rating', 0),
                'rating_count': p.get('userRatingCount', 0),
            })

        system_prompt = """You are a local business analyst. You classify businesses and generate descriptive tags.
Respond ONLY with a JSON object: {"results": [...]}. No extra text."""

        # Build the existing tags instruction
        existing_tags_block = ""
        if existing_tags_str:
            existing_tags_block = f"""
   REUSE these existing tags whenever they fit (STRONGLY PREFERRED over inventing new ones):
   {existing_tags_str}
   You may create a NEW tag only if none of the above apply. Keep new tags short (1-2 words)."""

        user_prompt = f"""For each business below, provide:

1. **is_small** (boolean): true = small, independent, locally-owned business. false = chain, franchise (McDonald's, Starbucks, Tim Hortons, Subway, Pizza Pizza, Walmart, Costco, etc.), big-box store, supermarket chain, bank, or large corporation.

2. **category** (string): Pick the BEST-FIT subcategory from this list:
{category_prompt}
Return the exact subcategory name (e.g. "Restaurants", "Beauty", "Auto"). If none fit well, return the parent category name.
You MUST use one of the exact names listed above. Do NOT invent new category names.

3. **tags** (array of strings): Generate 3-5 descriptive tags that help users DISCOVER this business.
   Tags should describe WHAT the business offers or its VIBE — not how good it is.
   Use short, reusable lowercase-hyphenated words (1-2 words max).
   GOOD tags (specific, searchable): "cozy", "pet-friendly", "wifi", "outdoor-seating", "vegan", "craft-beer", "late-night", "romantic", "artisan", "family-friendly", "takeout", "delivery", "organic", "brunch", "live-music", "quiet", "upscale", "casual", "trendy", "vintage", "handmade", "locally-sourced", "hidden-gem", "walk-in", "by-appointment", "sushi", "espresso", "yoga", "tattoo", "florist"
   BAD tags (NEVER use these kinds): "high-quality", "expert", "professional", "reliable", "trusted", "best", "great-service", "compassionate", "customer-satisfaction", "premium", "holistic", "athletic", "active", "awaiting-reviews", "basic-service", "children-friendly"
   RULE: A tag must answer "What can I find here?" or "What's the vibe?" — NOT "How good is it?"
   Do NOT generate tags about quality, ratings, expertise, or generic descriptors.{existing_tags_block}
   Every business should get at least 3 tags.

Return JSON: {{"results": [{{"id": "...", "is_small": true/false, "category": "...", "tags": [...]}}]}}

Businesses:
{json.dumps(batch_info, ensure_ascii=False)}"""

        try:
            response = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ],
                response_format={'type': 'json_object'},
                temperature=0.2,
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            if isinstance(parsed, list):
                ai_results = parsed
            elif isinstance(parsed, dict):
                ai_results = parsed.get('results', parsed.get('businesses', parsed.get('data', [])))
            else:
                ai_results = []
        except Exception as e:
            logger.error("AI classification error: %s", e)
            ai_results = [{'id': p.get('id', ''), 'is_small': True, 'category': '', 'tags': []} for p in batch]

        # Merge AI results with place data
        ai_map = {r['id']: r for r in ai_results if isinstance(r, dict) and 'id' in r}
        batch_results = []
        for p in batch:
            pid = p.get('id', '')
            ai = ai_map.get(pid, {'is_small': True, 'category': '', 'tags': []})
            batch_results.append({
                'place': p,
                'is_small': ai.get('is_small', True),
                'category': ai.get('category', ''),
                'tags': ai.get('tags', [])[:5],
            })
        return batch_results

    # 20 concurrent workers for AI classification
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(_classify_batch, b): i for i, b in enumerate(batches)}
        indexed_results = {}
        for future in as_completed(futures):
            idx = futures[future]
            try:
                indexed_results[idx] = future.result()
            except Exception as e:
                logger.error("AI classify worker error: %s", e)
                indexed_results[idx] = [
                    {'place': p, 'is_small': True, 'category': '', 'tags': []}
                    for p in batches[idx]
                ]
        # Reassemble in order
        for i in range(len(batches)):
            results.extend(indexed_results.get(i, []))

    return results, category_slug_map
