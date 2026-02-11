"""
DRF serializers — one class per model.

Serializers handle:
  • Field-level + object-level validation
  • JSON ↔ model conversion
  • Controlling which fields appear in requests/responses
"""
from rest_framework import serializers

from .models import (
    AutomationLog,
    Bookmark,
    Business,
    Category,
    Review,
    Reward,
    User,
    UserCoupon,
    UserProfile,
)


# ── User ───────────────────────────────────────────────────────────────────────
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'password_hash', 'role',
            'is_verified_human', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password_hash': {'write_only': True},
        }

    def create(self, validated_data):
        raw_password = validated_data.pop('password_hash', None)
        user = User(**validated_data)
        if raw_password:
            user.set_password(raw_password)
        user.save()
        return user

    def update(self, instance, validated_data):
        raw_password = validated_data.pop('password_hash', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if raw_password:
            instance.set_password(raw_password)
        instance.save()
        return instance


# ── UserProfile ────────────────────────────────────────────────────────────────
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'user', 'display_name', 'avatar_url', 'high_contrast',
            'keyboard_only_nav', 'persona_vector', 'loyalty_points', 'updated_at',
        ]
        read_only_fields = ['updated_at']


# ── Category ───────────────────────────────────────────────────────────────────
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon_name', 'updated_at']
        read_only_fields = ['id', 'updated_at']


# ── Business ───────────────────────────────────────────────────────────────────
class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = [
            'id', 'owner', 'category', 'name', 'description', 'address',
            'lat', 'lng', 'google_place_id', 'onboarding_status',
            'contact_email', 'avg_rating', 'review_count', 'metadata',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'avg_rating', 'review_count', 'created_at', 'updated_at']


# ── Review ─────────────────────────────────────────────────────────────────────
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'id', 'business', 'user', 'rating', 'content',
            'ai_fraud_score', 'is_visible', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ── Bookmark ───────────────────────────────────────────────────────────────────
class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'business', 'created_at']
        read_only_fields = ['id', 'created_at']


# ── Reward ─────────────────────────────────────────────────────────────────────
class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = [
            'id', 'provider_business', 'trigger_business', 'title',
            'description', 'discount_val', 'reward_type', 'expiry_date',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ── UserCoupon ─────────────────────────────────────────────────────────────────
class UserCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCoupon
        fields = ['id', 'user', 'reward', 'status', 'unlocked_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ── AutomationLog ─────────────────────────────────────────────────────────────
class AutomationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationLog
        fields = ['id', 'business', 'action_type', 'status', 'logged_at']
        read_only_fields = ['id', 'logged_at']
