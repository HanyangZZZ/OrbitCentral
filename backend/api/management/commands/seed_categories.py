"""
Seed the initial category hierarchy.

Categories are extendable — add new rows to the DB or new entries in this
command.  The AI prompt reads categories dynamically from the DB.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from api.models import Category

# (parent_name, icon_name, [subcategories])
CATEGORY_TREE = [
    ('Food & Drink', 'restaurant', [
        'Restaurants',
        'Fast Food',
        'Sweets',
        'Grocery',
    ]),
    ('Retail', 'storefront', [
        'Apparel & Accessories',
        'Home',
        'Gifts & Hobbies',
        'Electronics',
    ]),
    ('Entertainment', 'theater_comedy', [
        'Arts',
        'Recreation',
    ]),
    ('Personal Services', 'favorite', [
        'Health',
        'Beauty',
        'Education',
        'Pet Care',
    ]),
    ('Home Services', 'home_repair_service', [
        'Maintenance',
        'Cleaning',
        'Auto',
    ]),
]


class Command(BaseCommand):
    help = 'Seed the category hierarchy (idempotent — safe to run multiple times)'

    def handle(self, *args, **options):
        created_count = 0
        for parent_name, icon, children in CATEGORY_TREE:
            parent, p_created = Category.objects.get_or_create(
                slug=slugify(parent_name),
                defaults={'name': parent_name, 'icon_name': icon, 'parent': None},
            )
            if p_created:
                created_count += 1
                self.stdout.write(f'  + {parent_name}')

            for child_name in children:
                _, c_created = Category.objects.get_or_create(
                    slug=slugify(child_name),
                    defaults={'name': child_name, 'parent': parent},
                )
                if c_created:
                    created_count += 1
                    self.stdout.write(f'    + {child_name}')

        self.stdout.write(self.style.SUCCESS(
            f'Done — {created_count} new categories created'
        ))
