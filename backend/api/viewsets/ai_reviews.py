"""
AIReviewViewSet — AI-guided conversational review writing.

Endpoints:
  POST   /api/ai-reviews/start/          Start a chat session
  POST   /api/ai-reviews/<id>/message/   Send a message in the chat
  POST   /api/ai-reviews/<id>/generate/  Generate the final review description
  POST   /api/ai-reviews/<id>/confirm/   Confirm and create the actual Review
  GET    /api/ai-reviews/                List user's chat sessions
  GET    /api/ai-reviews/<id>/           Retrieve a chat session
  DELETE /api/ai-reviews/<id>/           Abandon a chat session
"""
import logging

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Business, Review
from ..models.review_chat import ReviewChat
from ..permissions import IsEmailVerified
from ..serializers.ai_review import (
    ReviewChatMessageSerializer,
    ReviewChatSerializer,
    ReviewChatStartSerializer,
)
from ..services.ai_review import (
    apply_tag_changes,
    continue_chat,
    generate_review_description,
    start_chat,
)

logger = logging.getLogger('api')


class AIReviewViewSet(viewsets.GenericViewSet):
    """
    AI-guided review writing through natural conversation.

    Flow:
        1. POST /api/ai-reviews/start/          → start session, get AI's first message
        2. POST /api/ai-reviews/<id>/message/    → chat back and forth (repeat)
        3. POST /api/ai-reviews/<id>/generate/   → AI writes the review description
        4. POST /api/ai-reviews/<id>/confirm/    → create the Review (+ optional photo)
    """
    serializer_class = ReviewChatSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified]
    lookup_field = 'pk'

    def get_queryset(self):
        return ReviewChat.objects.filter(user=self.request.user).select_related('business')

    # ── List user's chat sessions ──────────────────────────────────────────
    def list(self, request):
        """GET /api/ai-reviews/ — list current user's AI review sessions."""
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    # ── Retrieve a single session ──────────────────────────────────────────
    def retrieve(self, request, pk=None):
        """GET /api/ai-reviews/<id>/ — get a specific chat session."""
        session = self.get_object()
        serializer = self.get_serializer(session)
        return Response(serializer.data)

    # ── Delete (abandon) a session ────────────────────────────────────────
    def destroy(self, request, pk=None):
        """DELETE /api/ai-reviews/<id>/ — abandon a chat session."""
        session = self.get_object()
        session.status = 'abandoned'
        session.save(update_fields=['status'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ── Start a new chat session ───────────────────────────────────────────
    @action(detail=False, methods=['post'], url_path='start')
    def start(self, request):
        """
        Start an AI review chat session.

        POST /api/ai-reviews/start/
        {"business": 42, "rating": 4}

        Returns the chat session with the AI's opening message.
        """
        serializer = ReviewChatStartSerializer(
            data=request.data, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        business_id = serializer.validated_data['business']
        rating = serializer.validated_data['rating']
        business = Business.objects.get(pk=business_id)

        # Check for an existing active session for this business
        existing_session = ReviewChat.objects.filter(
            user=request.user,
            business=business,
            status='active',
        ).first()
        if existing_session:
            # Return the existing session instead of creating a new one
            return Response(
                ReviewChatSerializer(existing_session).data,
                status=status.HTTP_200_OK,
            )

        try:
            messages = start_chat(business, rating)
        except Exception as exc:
            logger.error('AI review chat start failed: %s', exc)
            return Response(
                {'detail': 'Failed to start AI chat. Please try again.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        session = ReviewChat.objects.create(
            user=request.user,
            business=business,
            rating=rating,
            messages=messages,
        )

        return Response(
            ReviewChatSerializer(session).data,
            status=status.HTTP_201_CREATED,
        )

    # ── Send a message ─────────────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='message')
    def message(self, request, pk=None):
        """
        Send a message in the AI review chat.

        POST /api/ai-reviews/<id>/message/
        {"message": "The pasta was incredible, super fresh"}

        Returns the updated conversation with the AI's response.
        """
        session = self.get_object()

        if session.status != 'active':
            return Response(
                {'detail': 'This chat session is no longer active.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        msg_serializer = ReviewChatMessageSerializer(data=request.data)
        msg_serializer.is_valid(raise_exception=True)
        user_message = msg_serializer.validated_data['message']

        try:
            updated_messages, assistant_reply, tags_added, tags_removed = continue_chat(
                messages=session.messages,
                user_message=user_message,
                business=session.business,
                rating=session.rating,
            )
        except Exception as exc:
            logger.error('AI review chat message failed: %s', exc)
            return Response(
                {'detail': 'AI assistant is temporarily unavailable. Please try again.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Update session
        session.messages = updated_messages
        if tags_added:
            session.tags_to_add = list(set(session.tags_to_add + tags_added))
        if tags_removed:
            session.tags_to_remove = list(set(session.tags_to_remove + tags_removed))
        session.save(update_fields=['messages', 'tags_to_add', 'tags_to_remove', 'updated_at'])

        return Response({
            'reply': assistant_reply,
            'tags_added': tags_added,
            'tags_removed': tags_removed,
            'session': ReviewChatSerializer(session).data,
        })

    # ── Generate the review description ───────────────────────────────────
    @action(detail=True, methods=['post'], url_path='generate')
    def generate(self, request, pk=None):
        """
        Generate the final review description from the conversation.

        POST /api/ai-reviews/<id>/generate/

        Returns the generated description. User can then confirm or ask to regenerate.
        """
        session = self.get_object()

        if session.status != 'active':
            return Response(
                {'detail': 'This chat session is no longer active.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len([m for m in session.messages if m.get('role') == 'user']) < 1:
            return Response(
                {'detail': 'Please chat with the AI first before generating a review.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            description = generate_review_description(
                messages=session.messages,
                business=session.business,
                rating=session.rating,
            )
        except Exception as exc:
            logger.error('AI review generation failed: %s', exc)
            return Response(
                {'detail': 'Failed to generate review. Please try again.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        session.generated_description = description
        session.save(update_fields=['generated_description', 'updated_at'])

        return Response({
            'generated_description': description,
            'session': ReviewChatSerializer(session).data,
        })

    # ── Confirm and create the actual Review ──────────────────────────────
    @action(detail=True, methods=['post'], url_path='confirm')
    def confirm(self, request, pk=None):
        """
        Confirm the AI-generated review and create the actual Review object.

        POST /api/ai-reviews/<id>/confirm/
        {
            "description": "...",   // optional override of generated text
            "photo": "base64..."    // optional photo, same as normal reviews
        }

        Creates a Review (same model as manual reviews) and marks session complete.
        """
        session = self.get_object()

        if session.status != 'active':
            return Response(
                {'detail': 'This chat session is no longer active.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not session.generated_description and not request.data.get('description'):
            return Response(
                {'detail': 'Generate a review description first, or provide your own.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check for duplicate review (same as normal review flow)
        existing = Review.objects.filter(
            user=request.user, business=session.business,
        ).first()
        if existing:
            return Response(
                {
                    'detail': 'You have already reviewed this business.',
                    'existing_review_id': existing.id,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Use provided description or the generated one
        description = request.data.get('description', session.generated_description)

        # Handle optional photo (reuse the same upload logic as ReviewViewSet)
        photo_b64 = request.data.get('photo')
        image_url = None
        if photo_b64:
            from ..viewsets.reviews import ReviewViewSet
            image_url = ReviewViewSet._upload_photo(photo_b64, session.business)

        # Create the Review
        review = Review.objects.create(
            user=request.user,
            business=session.business,
            rating=session.rating,
            description=description,
            image_url=image_url,
        )

        # Apply tag changes to the business
        apply_tag_changes(session.business, session.tags_to_add, session.tags_to_remove)

        # Mark session complete
        session.status = 'completed'
        session.review = review
        session.save(update_fields=['status', 'review', 'updated_at'])

        # Return the created review using ReviewSerializer
        from ..serializers import ReviewSerializer
        review_data = ReviewSerializer(review, context={'request': request}).data

        return Response(
            {
                'review': review_data,
                'tags_added': session.tags_to_add,
                'tags_removed': session.tags_to_remove,
            },
            status=status.HTTP_201_CREATED,
        )
