from django.contrib import admin

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


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ('id', 'email', 'role', 'is_verified_human', 'created_at')
	search_fields = ('email',)
	list_filter = ('role', 'is_verified_human')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'display_name', 'loyalty_points', 'high_contrast', 'keyboard_only_nav')
	search_fields = ('display_name', 'user__email')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'slug', 'icon_name')
	search_fields = ('name', 'slug')


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'category', 'avg_rating', 'review_count', 'onboarding_status')
	list_filter = ('onboarding_status', 'category')
	search_fields = ('name', 'google_place_id', 'contact_email')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	list_display = ('id', 'business', 'user', 'rating', 'ai_fraud_score', 'is_visible', 'created_at')
	list_filter = ('is_visible',)
	search_fields = ('content',)


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
	list_display = ('user', 'business', 'created_at')
	search_fields = ('user__email', 'business__name')


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'reward_type', 'provider_business', 'trigger_business', 'expiry_date')
	list_filter = ('reward_type',)
	search_fields = ('title',)


@admin.register(UserCoupon)
class UserCouponAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'reward', 'status', 'unlocked_at')
	list_filter = ('status',)


@admin.register(AutomationLog)
class AutomationLogAdmin(admin.ModelAdmin):
	list_display = ('id', 'business', 'action_type', 'status', 'logged_at')
	list_filter = ('status',)
