"""
Bookmark serializer.
"""
from rest_framework import serializers

from ..models import Bookmark


class BookmarkSerializer(serializers.ModelSerializer):
    """Serializer for user bookmarks."""
    username = serializers.CharField(source='user.username', read_only=True)
    business_name = serializers.CharField(source='business.name', read_only=True)

    class Meta:
        model = Bookmark
        fields = [
            'id', 'business', 'user', 'username', 'business_name',
            'note', 'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.method == 'POST':
            user = request.user
            business = attrs.get('business')
            if business and Bookmark.objects.filter(user=user, business=business).exists():
                raise serializers.ValidationError(
                    'You have already bookmarked this business.'
                )
        return attrs
