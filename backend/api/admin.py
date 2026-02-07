from django.contrib import admin

from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'rating', 'category', 'created_at')
	list_filter = ('category',)
	search_fields = ('name',)

# Register your models here.
