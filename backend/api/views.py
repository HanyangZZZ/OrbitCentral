import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Item


@csrf_exempt
def items(request):
	if request.method == 'POST':
		try:
			payload = json.loads(request.body.decode('utf-8') or '{}')
		except json.JSONDecodeError:
			return JsonResponse({'error': 'Invalid JSON.'}, status=400)

		name = payload.get('name')
		rating = payload.get('rating')
		category = payload.get('category')

		if not name or rating is None or not category:
			return JsonResponse({'error': 'name, rating, and category are required.'}, status=400)

		item = Item.objects.create(
			name=name,
			rating=float(rating),
			category=category,
		)

		return JsonResponse(
			{
				'item': {
					'id': item.id,
					'name': item.name,
					'rating': item.rating,
					'category': item.category,
				}
			},
			status=201,
		)

	if request.method != 'GET':
		return JsonResponse({'error': 'Method not allowed.'}, status=405)

	items = Item.objects.order_by('-created_at')
	return JsonResponse(
		{
			'items': [
				{
					'id': item.id,
					'name': item.name,
					'rating': item.rating,
					'category': item.category,
				}
				for item in items
			]
		}
	)

# Create your views here.
