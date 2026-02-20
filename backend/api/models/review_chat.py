"""
ReviewChat model — stores AI-guided review conversation sessions.

Each session tracks a multi-turn chat between a user and the AI assistant
that helps them write a review.  The final output is a standard Review
object (same model as manual reviews).
"""
import uuid

from django.conf import settings
from django.db import models


class ReviewChat(models.Model):
    """
    AI-guided review conversation session.

    Lifecycle:
        1. User starts a session (provides business + rating)
        2. AI asks guided questions (multiple message rounds)
        3. User confirms the generated description
        4. Session produces a Review object (same as manual reviews)
    """
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_chats',
    )
    business = models.ForeignKey(
        'api.Business',
        on_delete=models.CASCADE,
        related_name='review_chats',
    )
    rating = models.IntegerField(
        help_text='Star rating the user chose before starting the chat (1-5)',
    )
    messages = models.JSONField(
        default=list,
        help_text='Full conversation history [{role, content}, ...]',
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='active')

    # Tags the AI decided to add/remove during the conversation
    tags_to_add = models.JSONField(
        default=list, blank=True,
        help_text='Tag names the AI wants to ADD to the business',
    )
    tags_to_remove = models.JSONField(
        default=list, blank=True,
        help_text='Tag names the AI wants to REMOVE from the business',
    )

    # The final generated review text (set when conversation completes)
    generated_description = models.TextField(blank=True, default='')

    # If a Review was created from this session, keep the FK
    review = models.OneToOneField(
        'api.Review',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='chat_session',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'review_chats'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'ReviewChat({self.user}, {self.business.name}, {self.status})'
