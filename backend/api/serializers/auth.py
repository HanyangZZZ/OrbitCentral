"""
Auth / User serializers — UserProfile and Registration.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from ..models import UserProfile

User = get_user_model()


# ── User Profile ───────────────────────────────────────────────────────────────
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'username', 'email', 'display_name', 'avatar_url', 'bio',
            'email_verified', 'metadata', 'created_at', 'updated_at',
        ]
        read_only_fields = ['username', 'email', 'email_verified', 'created_at', 'updated_at']


# ── Registration ───────────────────────────────────────────────────────────────
class RegisterSerializer(serializers.Serializer):
    """
    Create a new User + UserProfile.  A verification email is sent async.
    """
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    display_name = serializers.CharField(max_length=150, required=False, default='')

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value.lower()

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        display_name = validated_data.pop('display_name', '')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        if display_name:
            user.profile.display_name = display_name
            user.profile.save(update_fields=['display_name'])
        return user
