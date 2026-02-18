from django.contrib import admin

from .models import (
	Bookmark, Business, Category, EmailVerificationToken,
	PasswordResetToken, Review, ReviewVote, SearchedArea, Tag, UserProfile,
)


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


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	list_display = ('id', 'business', 'user', 'rating', 'created_at')
	list_filter = ('rating', 'created_at')
	search_fields = ('business__name', 'user__username', 'description')
	raw_id_fields = ('business', 'user')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'display_name', 'email_verified', 'created_at')
	list_filter = ('email_verified',)
	search_fields = ('user__username', 'user__email', 'display_name')
	raw_id_fields = ('user',)


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'token', 'used', 'created_at', 'expires_at')
	list_filter = ('used',)
	search_fields = ('user__username', 'user__email', 'token')
	raw_id_fields = ('user',)


@admin.register(ReviewVote)
class ReviewVoteAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'review', 'vote_type', 'created_at')
	list_filter = ('vote_type', 'created_at')
	search_fields = ('user__username', 'review__business__name')
	raw_id_fields = ('user', 'review')


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'business', 'note', 'created_at')
	list_filter = ('created_at',)
	search_fields = ('user__username', 'business__name', 'note')
	raw_id_fields = ('user', 'business')


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'token', 'used', 'created_at', 'expires_at')
	list_filter = ('used',)
	search_fields = ('user__username', 'user__email', 'token')
	raw_id_fields = ('user',)
