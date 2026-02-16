from django.contrib import admin

from .models import Business, Category, SearchedArea, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'slug', 'icon_name')
	search_fields = ('name', 'slug')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'created_at')
	search_fields = ('name',)


@admin.register(SearchedArea)
class SearchedAreaAdmin(admin.ModelAdmin):
	list_display = ('id', 'radius_km', 'business_count', 'searched_at')
	list_filter = ('radius_km',)


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'category', 'avg_rating', 'review_count', 'business_status', 'onboarding_status')
	list_filter = ('onboarding_status', 'business_status', 'category')
	search_fields = ('name', 'google_place_id', 'contact_email', 'phone')
