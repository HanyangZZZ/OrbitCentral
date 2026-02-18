"""
Review serializer.
"""
from django.db import models as db_models
from rest_framework import serializers

from ..models import Review, ReviewVote


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for user-submitted reviews.
    - Accepts an optional `photo` field (base64-encoded image) on create/update.
    - Returns the GCS `image_url` publicly.
    - `username` is a read-only convenience field.
    - `vote_counts` and `user_votes` provide helpfulness data.
    """
    username = serializers.SerializerMethodField()
    photo = serializers.CharField(write_only=True, required=False, allow_blank=True)
    vote_counts = serializers.SerializerMethodField()
    user_votes = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'business', 'user', 'username', 'rating', 'description',
            'image_url', 'photo', 'vote_counts', 'user_votes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'image_url', 'created_at', 'updated_at']

    def get_username(self, obj):
        """Return username or 'Deleted User' for anonymized reviews."""
        if obj.user is None:
            return 'Deleted User'
        return obj.user.username

    def get_vote_counts(self, obj):
        """Aggregate vote counts by type."""
        counts = {'useful': 0, 'funny': 0, 'cool': 0}
        if hasattr(obj, '_prefetched_objects_cache') and 'votes' in obj._prefetched_objects_cache:
            for v in obj.votes.all():
                if v.vote_type in counts:
                    counts[v.vote_type] += 1
        else:
            qs = obj.votes.values('vote_type').annotate(c=db_models.Count('id'))
            for row in qs:
                counts[row['vote_type']] = row['c']
        return counts

    def get_user_votes(self, obj):
        """Return list of vote types the current user has cast on this review."""
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return []
        if hasattr(obj, '_prefetched_objects_cache') and 'votes' in obj._prefetched_objects_cache:
            return [v.vote_type for v in obj.votes.all() if v.user_id == request.user.id]
        return list(
            obj.votes.filter(user=request.user).values_list('vote_type', flat=True)
        )

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value

    def validate(self, attrs):
        """Prevent duplicate reviews (same user + same business)."""
        request = self.context.get('request')
        if request and request.method == 'POST':
            user = request.user
            business = attrs.get('business')
            if business and Review.objects.filter(user=user, business=business).exists():
                raise serializers.ValidationError(
                    'You have already reviewed this business. Edit or delete your existing review.'
                )
        return attrs
