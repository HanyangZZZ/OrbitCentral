from django.db import models


class AutomationLog(models.Model):
    business = models.ForeignKey(
        'api.Business', on_delete=models.SET_NULL,
        blank=True, null=True, related_name='automation_logs',
    )
    action_type = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'automation_logs'

    def __str__(self) -> str:
        return f"Log {self.id}"
