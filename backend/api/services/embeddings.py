"""
Embedding generation — create text-embedding-3-small vectors for businesses.
"""
import logging

from concurrent.futures import ThreadPoolExecutor, as_completed

import openai
from django.db import close_old_connections

from ..models import Business

logger = logging.getLogger('api')


def _generate_embeddings(client: openai.OpenAI, business_ids: list[int]):
    """
    Generate embeddings for businesses with tags baked into the text.
    Uses 4 concurrent workers to process batches in parallel.
    """
    if not business_ids:
        return

    businesses = list(
        Business.objects.filter(id__in=business_ids)
        .select_related('category', 'category__parent')
        .prefetch_related('tags')
    )

    batch_size = 100
    batches = [businesses[i:i + batch_size] for i in range(0, len(businesses), batch_size)]

    def _embed_batch(batch):
        close_old_connections()  # ensure fresh DB connection in thread
        texts = []
        for biz in batch:
            tag_str = ', '.join(t.name for t in biz.tags.all())
            cat_str = ''
            if biz.category:
                if biz.category.parent:
                    cat_str = f"{biz.category.parent.name} > {biz.category.name}"
                else:
                    cat_str = biz.category.name
            text = f"{biz.name}."
            if cat_str:
                text += f" Category: {cat_str}."
            if biz.description:
                text += f" {biz.description}"
            if tag_str:
                text += f" Tags: {tag_str}."
            if biz.address:
                text += f" Located at {biz.address}"
            texts.append(text.strip())

        try:
            response = client.embeddings.create(
                model='text-embedding-3-small',
                input=texts,
            )
            for j, item in enumerate(response.data):
                Business.objects.filter(id=batch[j].id).update(embedding=item.embedding)
        except Exception as e:
            logger.error("Embedding generation error: %s", e)

    # 4 concurrent workers for embedding generation
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(_embed_batch, b) for b in batches]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error("Embedding worker error: %s", e)
