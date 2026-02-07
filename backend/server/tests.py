from django.test import TestCase

from api.models import Item


class ItemsApiTests(TestCase):
    def setUp(self):
        Item.objects.create(name='Alpha', rating=4.5, category='A')
        Item.objects.create(name='Beta', rating=3.2, category='B')

    def test_get_items(self):
        response = self.client.get('/api/items/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['items']), 2)

    def test_create_item(self):
        response = self.client.post(
            '/api/items/',
            data={'name': 'Gamma', 'rating': 4.9, 'category': 'A'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        follow_up = self.client.get('/api/items/')
        self.assertEqual(len(follow_up.json()['items']), 3)

    def test_create_item_requires_fields(self):
        response = self.client.post(
            '/api/items/',
            data={'name': '', 'rating': 4.9},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
