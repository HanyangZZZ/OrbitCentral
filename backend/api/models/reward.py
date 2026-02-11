from django.db import models


class Reward(models.Model):
    provider_business = models.ForeignKey(
        'api.Business', on_delete=models.CASCADE, related_name='provided_rewards',
    )
    trigger_business = models.ForeignKey(
        'api.Business', on_delete=models.CASCADE,
        blank=True, null=True, related_name='triggered_rewards',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    discount_val = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    reward_type = models.CharField(
        max_length=20,
        choices=(
            ('dividend', 'Dividend'),
            ('standard_coupon', 'Standard Coupon'),
            ('quest_reward', 'Quest Reward'),
        ),
        blank=True, null=True,
    )
    expiry_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rewards'

    def __str__(self) -> str:
        return self.title


class UserCoupon(models.Model):
    user = models.ForeignKey(
        'api.User', on_delete=models.SET_NULL,
        blank=True, null=True, related_name='coupons',
    )
    reward = models.ForeignKey(
        Reward, on_delete=models.CASCADE, related_name='coupons',
    )
    status = models.CharField(
        max_length=20,
        choices=(
            ('locked', 'Locked'),
            ('unlocked', 'Unlocked'),
            ('redeemed', 'Redeemed'),
        ),
        default='locked',
    )
    unlocked_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_coupons'

    def __str__(self) -> str:
        return f"Coupon {self.id}"
