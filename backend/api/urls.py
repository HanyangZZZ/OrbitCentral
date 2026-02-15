from django.urls import path

from . import views

urlpatterns = [
    path('items/', views.items, name='items'),
    path('search/vibe/', views.vibe_search, name='vibe_search'),
    path('businesses/sort/', views.business_sort, name='business_sort'),
    path('bookmarks/status/', views.bookmark_status, name='bookmark_status'),
    path('bookmarks/toggle/', views.bookmark_toggle, name='bookmark_toggle'),
    path('bookmarks/grouped/', views.bookmarks_grouped, name='bookmarks_grouped'),
]
