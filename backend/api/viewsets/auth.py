"""
AuthViewSet — registration, login, email verification, password reset.
"""
import logging

from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import EmailVerificationToken, PasswordResetToken, Review, UserProfile
from ..serializers import RegisterSerializer, UserProfileSerializer
from ..services.captcha import verify_captcha
from ..authentication import AUTH_COOKIE_NAME, AUTH_COOKIE_MAX_AGE
from ..tasks import send_password_reset_email_task, send_verification_email_task

User = get_user_model()

logger = logging.getLogger('api')


class AuthViewSet(viewsets.GenericViewSet):
    """
    Authentication & user-management endpoints.

    Public:
      POST /api/auth/register/         — create account + send verification email
      POST /api/auth/login/            — obtain auth token
      POST /api/auth/verify-email/     — verify email with token

    Authenticated:
      GET    /api/auth/me/             — current user profile
      PATCH  /api/auth/me/             — update profile
      POST   /api/auth/resend-verify/  — resend verification email

    Password reset:
      POST /api/auth/forgot-password/  — request reset email
      POST /api/auth/reset-password/   — reset with token
    """
    serializer_class = UserProfileSerializer

    # ── Register ───────────────────────────────────────────────────────────
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny],
            url_path='register')
    def register(self, request):
        captcha = verify_captcha(request.data.get('captcha_token', ''), expected_action='register')
        if not captcha['success']:
            return Response({'detail': captcha['error']}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token, _ = Token.objects.get_or_create(user=user)

        vtoken = EmailVerificationToken.create_for_user(user)
        email_result = self._send_email_sync(
            send_verification_email_task, user.id, vtoken.token
        )

        response = Response({
            'token': token.key,
            'user': UserProfileSerializer(user.profile).data,
            'detail': 'Account created.',
            'email': email_result,
        }, status=status.HTTP_201_CREATED)
        if request.data.get('cookie_consent'):
            self._set_auth_cookie(response, token.key)
        return response

    # ── Login ──────────────────────────────────────────────────────────────
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny],
            url_path='login')
    def login(self, request):
        captcha = verify_captcha(request.data.get('captcha_token', ''), expected_action='login')
        if not captcha['success']:
            return Response({'detail': captcha['error']}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import authenticate

        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        user = authenticate(request, username=username, password=password)
        if not user:
            try:
                u = User.objects.get(email__iexact=username)
                user = authenticate(request, username=u.username, password=password)
            except User.DoesNotExist:
                pass

        if not user:
            return Response(
                {'detail': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, _ = Token.objects.get_or_create(user=user)
        profile, _ = UserProfile.objects.get_or_create(user=user)

        response = Response({
            'token': token.key,
            'user': UserProfileSerializer(profile).data,
        })
        if request.data.get('cookie_consent'):
            self._set_auth_cookie(response, token.key)
        return response

    # ── Verify Email ───────────────────────────────────────────────────────
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny],
            url_path='verify-email')
    def verify_email(self, request):
        token_str = request.data.get('token', '').strip()
        if not token_str:
            return Response(
                {'detail': 'Token is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            vtoken = EmailVerificationToken.objects.select_related('user').get(token=token_str)
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {'detail': 'Invalid or expired token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not vtoken.is_valid:
            return Response(
                {'detail': 'Token has expired or already been used.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        vtoken.used = True
        vtoken.save(update_fields=['used'])

        profile, _ = UserProfile.objects.get_or_create(user=vtoken.user)
        profile.email_verified = True
        profile.save(update_fields=['email_verified'])

        return Response({
            'detail': 'Email verified successfully.',
            'user': UserProfileSerializer(profile).data,
        })

    # ── Logout ──────────────────────────────────────────────────────────
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated],
            url_path='logout')
    def logout(self, request):
        """Delete the current auth token and clear the auth cookie."""
        Token.objects.filter(user=request.user).delete()
        response = Response({'detail': 'Logged out successfully.'}, status=status.HTTP_200_OK)
        response.delete_cookie(AUTH_COOKIE_NAME, path='/', samesite='Lax')
        return response

    # ── Me (profile) ───────────────────────────────────────────────────────
    @action(detail=False, methods=['get', 'patch', 'delete'], permission_classes=[permissions.IsAuthenticated],
            url_path='me')
    def me(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        if request.method == 'DELETE':
            return self._delete_account(request)

        if request.method == 'PATCH':
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        return Response(UserProfileSerializer(profile).data)

    def _delete_account(self, request):
        """
        Permanently delete the user account.

        Reviews are anonymized (user set to None, username shown as 'Deleted User')
        so ratings and review text are preserved for the community.
        Everything else (bookmarks, votes, tokens, profile) is cascade-deleted.
        """
        user = request.user

        # Anonymize reviews — keep the content, remove user association
        Review.objects.filter(user=user).update(user=None)

        # Delete auth tokens
        Token.objects.filter(user=user).delete()

        # Delete the Django User (cascades to profile, bookmarks, votes, verification tokens, etc.)
        user.delete()

        return Response(
            {'detail': 'Account deleted. Your reviews have been anonymized.'},
            status=status.HTTP_200_OK,
        )

    # ── Resend Verification ────────────────────────────────────────────────
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated],
            url_path='resend-verify')
    def resend_verify(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if profile.email_verified:
            return Response({'detail': 'Email is already verified.'})

        EmailVerificationToken.objects.filter(user=request.user, used=False).update(used=True)

        vtoken = EmailVerificationToken.create_for_user(request.user)
        email_result = self._send_email_sync(
            send_verification_email_task, request.user.id, vtoken.token
        )

        resp_status = status.HTTP_200_OK if email_result.get('status') == 'sent' else status.HTTP_502_BAD_GATEWAY
        return Response({
            'detail': 'Verification email sent.' if email_result.get('status') == 'sent' else 'Failed to send verification email.',
            'email': email_result,
        }, status=resp_status)

    # ── Helper: synchronous email send ───────────────────────────────────
    @staticmethod
    def _send_email_sync(task_func, *args):
        """
        Run the Celery email task **in-process** (no broker roundtrip) so the
        result is available immediately.  Brevo API typically responds in 1-2 s.
        """
        try:
            result = task_func.apply(args=args)
            if result.successful():
                return result.result
            return {'status': 'error', 'reason': str(result.result)}
        except Exception as exc:
            logger.warning("Email task failed: %s", exc)
            return {'status': 'error', 'reason': str(exc)}

    # ── Helper: set/clear auth cookie ──────────────────────────────────────
    @staticmethod
    def _set_auth_cookie(response, token_key):
        """Set HttpOnly auth cookie on the response."""
        import os
        secure = os.environ.get('SECURE_SSL_REDIRECT', 'false').lower() == 'true'
        response.set_cookie(
            AUTH_COOKIE_NAME,
            token_key,
            max_age=AUTH_COOKIE_MAX_AGE,
            httponly=True,
            secure=secure,
            samesite='Lax',
            path='/',
        )

    # ── Forgot Password ───────────────────────────────────────────────────
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny],
            url_path='forgot-password')
    def forgot_password(self, request):
        """
        Request a password-reset email.
        Always returns 200 regardless of whether the email exists (prevents enumeration).
        """
        captcha = verify_captcha(request.data.get('captcha_token', ''), expected_action='forgot_password')
        if not captcha['success']:
            return Response({'detail': captcha['error']}, status=status.HTTP_400_BAD_REQUEST)

        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response(
                {'detail': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email_result = None
        try:
            user = User.objects.get(email__iexact=email)
            PasswordResetToken.objects.filter(user=user, used=False).update(used=True)
            rtoken = PasswordResetToken.create_for_user(user)
            email_result = self._send_email_sync(
                send_password_reset_email_task, user.id, rtoken.token
            )
        except User.DoesNotExist:
            pass

        return Response({
            'detail': 'If an account with that email exists, a reset link has been sent.',
            'email': email_result,
        })

    # ── Reset Password ─────────────────────────────────────────────────────
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny],
            url_path='reset-password')
    def reset_password(self, request):
        """
        Reset password using a token from the password-reset email.
        On success, all existing auth tokens for the user are deleted (force re-login).
        """
        from django.contrib.auth.password_validation import validate_password as django_validate

        token_str = request.data.get('token', '').strip()
        new_password = request.data.get('new_password', '')

        if not token_str or not new_password:
            return Response(
                {'detail': 'Both token and new_password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            rtoken = PasswordResetToken.objects.select_related('user').get(token=token_str)
        except PasswordResetToken.DoesNotExist:
            return Response(
                {'detail': 'Invalid or expired token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not rtoken.is_valid:
            return Response(
                {'detail': 'Token has expired or already been used.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            django_validate(new_password, user=rtoken.user)
        except Exception as e:
            return Response(
                {'detail': list(e.messages)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rtoken.used = True
        rtoken.save(update_fields=['used'])

        rtoken.user.set_password(new_password)
        rtoken.user.save()

        Token.objects.filter(user=rtoken.user).delete()

        return Response({'detail': 'Password reset successfully. Please log in with your new password.'})
