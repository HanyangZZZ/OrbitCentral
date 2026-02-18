"""
Tag resolution — normalize, deduplicate, and consolidate AI-generated tags
using OpenAI-powered semantic consolidation.
"""
import json
import logging

import openai

from ..models import Tag

logger = logging.getLogger('api')

# ── Blocklist — generic/quality descriptors that don't help discovery ──────────
BLOCKLIST = frozenset({
    'local', 'unique', 'quality', 'professional', 'reliable',
    'popular', 'convenient', 'friendly', 'community', 'affordable',
    'modern', 'traditional', 'diverse', 'authentic', 'creative',
    'welcoming', 'specialty', 'essential', 'trusted', 'established',
    'neighborhood', 'neighbourhood', 'accessible', 'custom', 'curated',
    'premium', 'fresh', 'homemade', 'healthy', 'natural', 'expert',
    'personalized', 'innovative', 'comfortable', 'spacious',
    'clean', 'fast', 'small-batch', 'independent', 'new',
    'service', 'quick', 'refined', 'hearty', 'flexible',
    'gift', 'gifts', 'gear', 'indoor', 'relaxed', 'fast-service',
    'multi-service', 'customer-favorite', 'local-favorite',
    'concierge', 'organization', 'restoration',
    'adorable', 'whimsical', 'simple', 'flavored', 'experienced',
    'quick-service', 'cultural', 'detailed', 'luxurious', 'elegant',
    'classic', 'stylish', 'chic', 'lovely', 'pleasant', 'warm',
    'bright', 'cozy-spot', 'nice', 'good', 'great', 'best',
    'delicious', 'tasty', 'yummy', 'savory', 'flavorful',
    'efficient', 'dependable', 'unique-finds', 'local-business',
    'skilled', 'dedicated', 'reputable', 'responsive', 'thorough',
    # generic service/quality descriptors
    'basic-service', 'expert-service', 'customer-satisfaction',
    'compassionate', 'active', 'durable', 'replacement',
    'satisfaction', 'comprehensive', 'attentive', 'exceptional',
    'specialized', 'certified', 'licensed', 'insured',
    'consultation', 'assessment', 'estimate', 'diagnosis',
    'maintenance', 'installation', 'inspection',
    # more generic descriptors
    'high-rated', 'customer-service', 'premium-quality', 'caring',
    'expert-repair', 'premier', 'fine', 'programs', 'rental',
    'high-rating', 'awaiting-reviews', 'active-lifestyle',
    'basic-services', 'expert-advice', 'high-quality',
    'holistic', 'athletic', 'food-delivery',
})

# ── Suffixes to strip during normalization ─────────────────────────────────────
_STRIP_SUFFIXES = [
    '-atmosphere', '-ambiance', '-ambience', '-setting', '-vibes', '-vibe',
    '-experience', '-style', '-inspired', '-oriented', '-based', '-focused',
    '-options', '-menu', '-selection', '-offerings',
]


def _normalize_tag(name: str) -> str:
    """Normalize tag to a canonical short form before vector dedup."""
    clean = name.lower().strip()
    for suffix in _STRIP_SUFFIXES:
        if clean.endswith(suffix) and len(clean) > len(suffix) + 2:
            clean = clean[:len(clean) - len(suffix)]
            break
    return clean


def _is_blocked(norm: str) -> bool:
    """Check if a normalized tag should be blocked (handles plurals)."""
    if norm in BLOCKLIST:
        return True
    # Check singular form (strip trailing 's')
    if norm.endswith('s') and not norm.endswith('ss') and norm[:-1] in BLOCKLIST:
        return True
    # Check compound singular: "basic-services" → "basic-service"
    if '-' in norm:
        parts = norm.rsplit('-', 1)
        singular = parts[0] + '-' + parts[1].rstrip('s') if parts[1].endswith('s') and not parts[1].endswith('ss') else None
        if singular and singular in BLOCKLIST:
            return True
    return False


def _resolve_tags(client: openai.OpenAI, tag_names: list[str]) -> dict[str, Tag]:
    """
    Resolve raw AI-generated tags into a compact canonical set using
    OpenAI-powered consolidation instead of vector cosine similarity.

    Strategy:
      1. Normalize + blocklist filter (fast, no API cost)
      2. Load existing tags from DB
      3. Send candidates + existing tags to GPT-4o-mini for consolidation
      4. Create Tag objects for genuinely new canonical tags
      5. Generate vector embeddings for new tags (kept for user search)

    Returns a dict mapping original tag name → Tag model instance.
    """
    if not tag_names:
        return {}

    # ── Step 0: blocklist + normalize ──────────────────────────────────────
    filtered_names: list[str] = []
    norm_map: dict[str, str] = {}   # original_name → normalized
    unique_norms: set[str] = set()

    for name in tag_names:
        norm = _normalize_tag(name)
        if not _is_blocked(norm) and len(norm) >= 2 and norm.count('-') <= 1:
            filtered_names.append(name)
            norm_map[name] = norm
            unique_norms.add(norm)

    if not unique_norms:
        return {}

    sorted_norms = sorted(unique_norms)
    blocked_count = len(tag_names) - len(filtered_names)
    logger.info("Tags: %d raw → %d filtered → %d unique (blocked %d)",
                len(tag_names), len(filtered_names), len(sorted_norms), blocked_count)

    # ── Step 1: load existing tags from DB ─────────────────────────────────
    existing_tags = list(Tag.objects.values_list('name', flat=True))

    # ── Step 2: OpenAI consolidation ───────────────────────────────────────
    consolidation = _consolidate_tags_with_ai(client, sorted_norms, existing_tags)

    # Post-consolidation: filter canonical values through blocklist
    for candidate, canonical in list(consolidation.items()):
        if _is_blocked(canonical) and canonical != candidate:
            consolidation[candidate] = candidate  # revert to original
        elif _is_blocked(canonical) and _is_blocked(candidate):
            del consolidation[candidate]  # drop both

    canonical_names = set(consolidation.values())
    merged_count = len(sorted_norms) - len(canonical_names)
    logger.info("AI consolidation: %d candidates → %d canonical (%d merged)",
                len(sorted_norms), len(canonical_names), merged_count)

    # ── Step 3: get-or-create Tag objects ──────────────────────────────────
    existing_objs = {t.name: t for t in Tag.objects.filter(name__in=canonical_names)}
    new_tag_names = [n for n in canonical_names if n not in existing_objs]

    new_tags_created = []
    for name in new_tag_names:
        tag, created = Tag.objects.get_or_create(name=name)
        existing_objs[name] = tag
        if created:
            new_tags_created.append(tag)

    # ── Step 4: generate embeddings for new tags ──────────────────────────
    needs_embedding = [t for t in new_tags_created if t.embedding is None]
    if needs_embedding:
        embed_names = [t.name for t in needs_embedding]
        try:
            resp = client.embeddings.create(
                model='text-embedding-3-small',
                input=embed_names,
            )
            for i, item in enumerate(resp.data):
                needs_embedding[i].embedding = item.embedding
                needs_embedding[i].save(update_fields=['embedding'])
        except Exception as e:
            logger.error("Tag embedding error: %s", e)

    logger.info("Tags resolved: %d new created, %d total in DB",
                len(new_tags_created), Tag.objects.count())

    # ── Step 5: map original names → Tag objects ──────────────────────────
    result: dict[str, Tag] = {}
    for original_name in filtered_names:
        norm = norm_map[original_name]
        canonical = consolidation.get(norm, norm)
        tag = existing_objs.get(canonical)
        if tag:
            result[original_name] = tag

    return result


# ── AI tag consolidation ───────────────────────────────────────────────────────

FORBIDDEN_CANONICALS = frozenset({
    'vibe', 'food', 'art', 'services', 'health', 'beauty', 'cuisine',
    'drinks', 'quality', 'business', 'space', 'location', 'shopping',
    'healthcare', 'treatments', 'grooming', 'auto', 'entertainment',
    'dining', 'wellness', 'fitness', 'lifestyle', 'retail', 'culture',
    'recreation', 'hospitality', 'maintenance', 'personal-care',
    'food-and-drink', 'arts-and-crafts', 'health-and-wellness',
    'event', 'restaurant', 'local-service', 'community',
})


def _consolidate_tags_with_ai(
    client: openai.OpenAI,
    candidate_tags: list[str],
    existing_tags: list[str],
) -> dict[str, str]:
    """
    Consolidate candidate tags into a smaller canonical set using GPT-4o-mini.
    Processes in batches of ~100 for better accuracy.
    """
    BATCH_SIZE = 100

    all_mappings: dict[str, str] = {}
    reference_tags = set(existing_tags)

    sorted_candidates = sorted(candidate_tags)
    total_batches = (len(sorted_candidates) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_idx in range(total_batches):
        start = batch_idx * BATCH_SIZE
        batch = sorted_candidates[start:start + BATCH_SIZE]

        batch_mappings = _consolidate_batch(
            client, batch, sorted(reference_tags), batch_idx + 1, total_batches,
        )

        # Post-processing: revert forbidden super-category canonicals
        for candidate, canonical in list(batch_mappings.items()):
            if canonical in FORBIDDEN_CANONICALS:
                if candidate in FORBIDDEN_CANONICALS:
                    del batch_mappings[candidate]
                else:
                    batch_mappings[candidate] = candidate

        all_mappings.update(batch_mappings)
        reference_tags.update(batch_mappings.values())

    merged = sum(1 for c, v in all_mappings.items() if c != v)
    canonical_count = len(set(all_mappings.values()))
    logger.info("AI consolidation: %d candidates → %d canonical (%d merged) in %d batches",
                len(candidate_tags), canonical_count, merged, total_batches)
    return all_mappings


def _consolidate_batch(
    client: openai.OpenAI,
    batch_candidates: list[str],
    reference_tags: list[str],
    batch_num: int,
    total_batches: int,
) -> dict[str, str]:
    """Consolidate a single batch of ~100 candidates against the reference tags."""
    ref_str = ', '.join(reference_tags) if reference_tags else '(none yet)'
    cand_str = ', '.join(batch_candidates)

    system = (
        "You consolidate tags for a local business discovery app. "
        "You AGGRESSIVELY merge synonyms, near-duplicates, and compounds into the "
        "EXISTING reference set. You keep genuinely distinct concepts. "
        "Output ONLY JSON."
    )

    user = f"""Map each CANDIDATE tag to the best REFERENCE tag, or keep as-is ONLY if truly unique.

MERGE AGGRESSIVELY:
1. Morphological variants → pick ONE:  relaxing→relaxation, artisanal→artisan, cozy→cozy (not coziness)
2. Compounds → base:  handmade-glass→handmade, custom-care→custom, canadian-cuisine→canadian
3. Near-synonyms:  comfy→cozy, hip→trendy, laid-back→casual, eatery→restaurant, doggy→pet-friendly
4. Same service:  nail-art→nail-care, hair-salon→hair-care, brake-repair→auto-repair, patio→outdoor-seating
5. If a REFERENCE tag already covers this concept, USE IT. Prefer existing reference tags.

KEEP SEPARATE only when truly different user search intents (cozy≠trendy, japanese≠italian, wifi≠delivery).

NEVER output: vibe, food, art, services, health, beauty, cuisine, drinks, business, space, shopping, auto, lifestyle

REFERENCE TAGS ({len(reference_tags)}):
[{ref_str}]

CANDIDATES (batch {batch_num}/{total_batches}, {len(batch_candidates)} tags):
[{cand_str}]

Return JSON: {{"mappings": {{"candidate": "canonical", ...}}}}
Every candidate MUST appear as key. Prefer mapping to reference tags."""

    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': user},
            ],
            response_format={'type': 'json_object'},
            temperature=0.1,
        )
        parsed = json.loads(response.choices[0].message.content)
        mappings = parsed.get('mappings', {})

        for tag in batch_candidates:
            if tag not in mappings:
                mappings[tag] = tag

        batch_merged = sum(1 for c, v in mappings.items() if c != v)
        logger.info("  Batch %d/%d: %d candidates → %d merged",
                     batch_num, total_batches, len(batch_candidates), batch_merged)
        return mappings

    except Exception as e:
        logger.error("Batch %d consolidation error: %s — identity fallback", batch_num, e)
        return {t: t for t in batch_candidates}
