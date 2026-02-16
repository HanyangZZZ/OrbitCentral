"""
Management command: generate vector embeddings for businesses that don't have one.

Usage:
    python manage.py generate_embeddings          # embed all missing
    python manage.py generate_embeddings --all    # re-embed everything
"""
import os
import time

from django.core.management.base import BaseCommand

import openai


class Command(BaseCommand):
    help = 'Generate OpenAI embeddings for businesses missing the embedding field.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all', action='store_true',
            help='Re-generate embeddings for ALL businesses, not just missing ones.',
        )
        parser.add_argument(
            '--batch-size', type=int, default=50,
            help='Number of businesses to embed per API call (default 50).',
        )

    def handle(self, *args, **options):
        from api.models import Business

        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        if not os.environ.get('OPENAI_API_KEY'):
            self.stderr.write(self.style.ERROR('OPENAI_API_KEY is not set.'))
            return

        qs = Business.objects.all()
        if not options['all']:
            qs = qs.filter(embedding__isnull=True)

        businesses = list(qs.values_list('id', 'name', 'description'))
        total = len(businesses)

        if total == 0:
            self.stdout.write(self.style.SUCCESS('All businesses already have embeddings.'))
            return

        self.stdout.write(f'Generating embeddings for {total} businesses...')

        batch_size = options['batch_size']
        updated = 0

        for i in range(0, total, batch_size):
            batch = businesses[i:i + batch_size]
            texts = [
                f"{name}. {desc or ''}" for _, name, desc in batch
            ]

            try:
                response = client.embeddings.create(
                    model='text-embedding-3-small',
                    input=texts,
                )
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'OpenAI API error: {e}'))
                break

            for j, item in enumerate(response.data):
                biz_id = batch[j][0]
                Business.objects.filter(id=biz_id).update(embedding=item.embedding)
                updated += 1

            self.stdout.write(f'  Embedded {min(i + batch_size, total)}/{total}')

            # Respect rate limits
            if i + batch_size < total:
                time.sleep(0.5)

        self.stdout.write(self.style.SUCCESS(f'Done. Updated {updated} businesses.'))
