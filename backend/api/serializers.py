"""
DRF serializers — Category & Business only (other models deferred).
"""
from rest_framework import serializers

from .models import Business, Category, Tag


# ── Tag ────────────────────────────────────────────────────────────────────────
class TagSerializer(serializers.ModelSerializer):
    usage_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Tag
        fields = ['id', 'name', 'usage_count']
        read_only_fields = ['id']


# ── Category ───────────────────────────────────────────────────────────────────
class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon_name', 'parent', 'parent_name', 'updated_at']
        read_only_fields = ['id', 'updated_at']

    def get_parent_name(self, obj):
        return obj.parent.name if obj.parent else None


# ── Business ───────────────────────────────────────────────────────────────────
class BusinessSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    latitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    longitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = [
            'id', 'category', 'category_detail', 'name', 'description', 'address', 'image_url',
            'contact_email', 'google_place_id',
            'phone', 'website_url', 'google_types', 'price_level',
            'photo_references', 'business_status',
            'onboarding_status', 'tags',
            'latitude', 'longitude', 'lat', 'lng',
            'avg_rating', 'review_count', 'user_rating_count', 'metadata',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'avg_rating', 'review_count', 'user_rating_count', 'created_at', 'updated_at']

    def get_lat(self, obj):
        return obj.location.y if obj.location else None

    def get_lng(self, obj):
        return obj.location.x if obj.location else None

    def create(self, validated_data):
        lat = validated_data.pop('latitude', None)
        lng = validated_data.pop('longitude', None)
        if lat is not None and lng is not None:
            from django.contrib.gis.geos import Point
            validated_data['location'] = Point(lng, lat, srid=4326)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        lat = validated_data.pop('latitude', None)
        lng = validated_data.pop('longitude', None)
        if lat is not None and lng is not None:
            from django.contrib.gis.geos import Point
            validated_data['location'] = Point(lng, lat, srid=4326)
        return super().update(instance, validated_data)


# ── Weighted search result ─────────────────────────────────────────────────────
class BusinessSearchSerializer(BusinessSerializer):
    """
    Extends BusinessSerializer with search scoring fields.
    - similarity: raw cosine similarity (0–1)
    - distance_km: distance from user in kilometres (null if no user location)
    - score: final weighted score (0–1), or null when an override sort is used
    """
    similarity = serializers.FloatField(read_only=True)
    distance_km = serializers.FloatField(read_only=True, default=None)
    score = serializers.FloatField(read_only=True, default=None)

    class Meta(BusinessSerializer.Meta):
        fields = BusinessSerializer.Meta.fields + ['similarity', 'distance_km', 'score']
