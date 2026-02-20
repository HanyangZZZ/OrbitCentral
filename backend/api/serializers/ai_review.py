"""
AI Review Chat serializers.
"""
from rest_framework import serializers

from ..models import Review
from ..models.review_chat import ReviewChat


class ReviewChatStartSerializer(serializers.Serializer):
    """Validate the initial request to start an AI review chat."""
    business = serializers.IntegerField(help_text='Business ID to review')
    rating = serializers.IntegerField(min_value=1, max_value=5, help_text='Star rating (1-5)')

    def validate_business(self, value):
        from ..models import Business
        try:
            Business.objects.get(pk=value)
        except Business.DoesNotExist:
            raise serializers.ValidationError('Business not found.')
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        if request:
            user = request.user
            business_id = attrs['business']
            # Check for existing review (same constraint as normal reviews)
            existing = Review.objects.filter(user=user, business_id=business_id).first()
            if existing:
                raise serializers.ValidationError({
                    'detail': 'You have already reviewed this business.',
                    'existing_review_id': existing.id,
                })
        return attrs


class ReviewChatMessageSerializer(serializers.Serializer):
    """Validate a user message in the chat."""
    message = serializers.CharField(
        max_length=2000,
        help_text='User message to the AI assistant',
    )


class ReviewChatSerializer(serializers.ModelSerializer):
    """Read-only serializer for the chat session state."""
    business_name = serializers.CharField(source='business.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    # Only expose user-visible messages (filter out system + tool messages)
    conversation = serializers.SerializerMethodField()

    class Meta:
        model = ReviewChat
        fields = [
            'id', 'business', 'business_name', 'user', 'username',
            'rating', 'status', 'conversation',
            'tags_to_add', 'tags_to_remove',
            'generated_description', 'review',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_conversation(self, obj):
        """Return only user-visible messages (no system/tool messages)."""
        if not obj.messages:
            return []
        visible = []
        for m in obj.messages:
            role = m.get('role')
            content = m.get('content', '')
            if role in ('assistant', 'user') and content:
                visible.append({'role': role, 'content': content})
        return visible
