import json

from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Item


# NOTE: Placeholder bookmark store.
# In production this should live in the DB with a Bookmark model.
_BOOKMARKS = set()  # {(user_id, business_id)}


def _master_category_for_business_id(business_id: str) -> str:
	"""Very small placeholder mapping from business_id/slug to the master categories.

	In production we'd look up the Business record + its category.
	"""
	slug = (business_id or '').lower()
	if any(key in slug for key in ['cafe', 'brew', 'bakery', 'food', 'drink', 'restaurant']):
		return 'Food'
	if any(key in slug for key in ['library', 'book', 'study', 'cowork']):
		return 'Education/Public Space'
	if any(key in slug for key in ['salon', 'trim', 'spa', 'wellness', 'massage']):
		return 'Services'
	return 'Retail'


def _infer_tags_for_business_id(business_id: str) -> list[str]:
	"""Placeholder tag inference using the slug.

	In production we'd use stored tags + review NLP.
	"""
	slug = (business_id or '').lower()
	tags = []
	if any(key in slug for key in ['quiet', 'library', 'study', 'focus', 'book']):
		tags.append('Quiet Workspaces')
	if any(key in slug for key in ['pet', 'paws', 'tails']):
		tags.append('Pet-Friendly Cafes')
	if any(key in slug for key in ['wifi', 'work', 'focus', 'cowork']):
		tags.append('Work-friendly')
	return tags


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


@csrf_exempt
def vibe_search(request):
	if request.method != 'POST':
		return JsonResponse({'error': 'Method not allowed.'}, status=405)

	try:
		payload = json.loads(request.body.decode('utf-8') or '{}')
	except json.JSONDecodeError:
		return JsonResponse({'error': 'Invalid JSON.'}, status=400)

	query = (payload.get('query') or '').strip()
	if not query:
		return JsonResponse({'tags': [], 'items': [], 'message': 'No query provided.'})

	keywords = {
		'quiet': 'Quiet',
		'work': 'Work-friendly',
		'coffee': 'Coffee',
		'cafe': 'Cafe',
		'tour': 'Tours',
		'hotel': 'Hotels',
		'fitness': 'Fitness',
		'wellness': 'Wellness',
		'massage': 'Massage',
		'karaoke': 'Karaoke',
	}

	query_lower = query.lower()
	tags = sorted({tag for key, tag in keywords.items() if key in query_lower})

	matched_items = Item.objects.filter(
		models.Q(name__icontains=query) | models.Q(category__icontains=query)
	).order_by('-created_at')

	return JsonResponse(
		{
			'tags': tags,
			'items': [
				{
					'id': item.id,
					'name': item.name,
					'rating': item.rating,
					'category': item.category,
				}
				for item in matched_items
			],
			'message': f'Results for "{query}".'
		}
	)


@csrf_exempt
def business_sort(request):
	"""Placeholder endpoint for frontend sort actions.

	Contract:
	- POST /api/businesses/sort/
	- Body: { sort: 'highest_rated' | 'rating' | 'recommended', category?: str, query?: str }
	- Response: { ok: bool, sort: str, received: {...}, items: [...] }

	For now we return Items from the DB (if any) so the endpoint is real,
	but the frontend still uses local placeholder business data.
	"""
	if request.method != 'POST':
		return JsonResponse({'error': 'Method not allowed.'}, status=405)

	try:
		payload = json.loads(request.body.decode('utf-8') or '{}')
	except json.JSONDecodeError:
		return JsonResponse({'error': 'Invalid JSON.'}, status=400)

	sort_mode = (payload.get('sort') or 'recommended').strip()
	query = (payload.get('query') or '').strip()
	category = (payload.get('category') or '').strip()

	qs = Item.objects.all()
	if query:
		qs = qs.filter(models.Q(name__icontains=query) | models.Q(category__icontains=query))
	if category:
		qs = qs.filter(category__icontains=category)

	if sort_mode in {'highest_rated', 'rating'}:
		qs = qs.order_by('-rating', '-created_at')
	else:
		qs = qs.order_by('-created_at')

	items = [
		{
			'id': item.id,
			'name': item.name,
			'rating': item.rating,
			'category': item.category,
		}
		for item in qs[:50]
	]

	return JsonResponse(
		{
			'ok': True,
			'sort': sort_mode,
			'received': {
				'sort': sort_mode,
				'query': query,
				'category': category,
			},
			'items': items,
		}
	)


@csrf_exempt
def bookmark_status(request):
	"""Check if a business is bookmarked by a user.

	Contract (placeholder):
	- POST /api/bookmarks/status/
	- Body: { userId: number|string, businessId: string }
	- Response: { bookmarked: bool }
	"""
	if request.method != 'POST':
		return JsonResponse({'error': 'Method not allowed.'}, status=405)

	try:
		payload = json.loads(request.body.decode('utf-8') or '{}')
	except json.JSONDecodeError:
		return JsonResponse({'error': 'Invalid JSON.'}, status=400)

	user_id = payload.get('userId')
	business_id = payload.get('businessId')
	if user_id is None or not business_id:
		return JsonResponse({'error': 'userId and businessId are required.'}, status=400)

	key = (str(user_id), str(business_id))
	return JsonResponse({'bookmarked': key in _BOOKMARKS})


@csrf_exempt
def bookmark_toggle(request):
	"""Set/unset bookmark state for a business.

	Contract (placeholder):
	- POST /api/bookmarks/toggle/
	- Body: { userId: number|string, businessId: string, bookmarked?: bool }
	- Response: { bookmarked: bool }
	"""
	if request.method != 'POST':
		return JsonResponse({'error': 'Method not allowed.'}, status=405)

	try:
		payload = json.loads(request.body.decode('utf-8') or '{}')
	except json.JSONDecodeError:
		return JsonResponse({'error': 'Invalid JSON.'}, status=400)

	user_id = payload.get('userId')
	business_id = payload.get('businessId')
	if user_id is None or not business_id:
		return JsonResponse({'error': 'userId and businessId are required.'}, status=400)

	key = (str(user_id), str(business_id))
	requested = payload.get('bookmarked')
	if requested is None:
		# toggle
		if key in _BOOKMARKS:
			_BOOKMARKS.remove(key)
			requested = False
		else:
			_BOOKMARKS.add(key)
			requested = True
	else:
		if bool(requested):
			_BOOKMARKS.add(key)
		else:
			_BOOKMARKS.discard(key)
		requested = bool(requested)

	return JsonResponse({'bookmarked': requested})


@csrf_exempt
def bookmarks_grouped(request):
	"""Return a user's bookmarks grouped by master categories + tag clusters.

	Contract (placeholder):
	- POST /api/bookmarks/grouped/
	- Body: { userId: number|string }
	- Response:
	  {
	    userId: "442",
	    groups: {
	      "Food": { "businessIds": [...], "tagGroups": {"Quiet Workspaces": [...] } },
	      ...
	    },
	    aiMessage: "..."
	  }
	"""
	if request.method != 'POST':
		return JsonResponse({'error': 'Method not allowed.'}, status=405)

	try:
		payload = json.loads(request.body.decode('utf-8') or '{}')
	except json.JSONDecodeError:
		return JsonResponse({'error': 'Invalid JSON.'}, status=400)

	user_id = payload.get('userId')
	if user_id is None:
		return JsonResponse({'error': 'userId is required.'}, status=400)

	uid = str(user_id)
	business_ids = [bid for (u, bid) in _BOOKMARKS if u == uid]

	groups: dict[str, dict] = {}
	tag_counts: dict[str, int] = {}

	for bid in business_ids:
		master = _master_category_for_business_id(bid)
		if master not in groups:
			groups[master] = {'businessIds': [], 'tagGroups': {}}
		groups[master]['businessIds'].append(bid)

		for tag in _infer_tags_for_business_id(bid):
			tag_counts[tag] = tag_counts.get(tag, 0) + 1
			tag_groups = groups[master]['tagGroups']
			tag_groups.setdefault(tag, []).append(bid)

	# AI suggestion (placeholder)
	ai_message = 'Save a few favorites to get AI suggestions.'
	if tag_counts:
		top_tag = sorted(tag_counts.items(), key=lambda kv: kv[1], reverse=True)[0][0]
		ai_message = f"I see you've saved {tag_counts[top_tag]} '{top_tag}'. Would you like to see more businesses with that tag?"

	return JsonResponse({'userId': uid, 'groups': groups, 'aiMessage': ai_message})

# Create your views here.
