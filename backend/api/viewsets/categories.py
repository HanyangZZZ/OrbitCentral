"""
CategoryViewSet — CRUD for business categories.
"""
from rest_framework import viewsets

from ..models import Category
from ..serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.order_by('name')
    serializer_class = CategorySerializer
    search_fields = ['name', 'slug']
