import base64
import requests
from decouple import config

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings

from .serializers import RegisterSerializer, UserSerializer, UpdateProfileSerializer
from .models import User

# ── Register ──────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Account created successfully',
            'user': UserSerializer(user, context={'request': request}).data,
            'tokens': {
                'access':  str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ── Login ─────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email    = request.data.get('email')
    password = request.data.get('password')
    role     = request.data.get('role')
    user     = authenticate(request, username=email, password=password)
    if not user:
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
    if role and user.role != role:
        return Response({'error': f'Access denied. This account is not registered as {role}.'}, status=status.HTTP_403_FORBIDDEN)
    refresh = RefreshToken.for_user(user)
    return Response({
        'message': 'Login successful',
        'user': UserSerializer(user, context={'request': request}).data,
        'tokens': {
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
        }
    })

# ── Profile (GET + UPDATE) ────────────────────────────────
@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def profile(request):
    if request.method == 'GET':
        return Response(UserSerializer(request.user, context={'request': request}).data)

    serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profile updated successfully',
            'user': UserSerializer(request.user, context={'request': request}).data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ── Upload Avatar ─────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_avatar(request):
    if 'avatar' not in request.FILES:
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
    file = request.FILES['avatar']
    if file.size > 2 * 1024 * 1024:
        return Response({'error': 'File must be under 2MB'}, status=status.HTTP_400_BAD_REQUEST)

    content_type = file.content_type or 'image/jpeg'
    encoded = base64.b64encode(file.read()).decode('utf-8')
    request.user.avatar_base64 = f"data:{content_type};base64,{encoded}"
    request.user.save()

    return Response({
        'message': 'Avatar uploaded successfully',
        'avatar_url': UserSerializer(request.user, context={'request': request}).data['avatar_url']
    })

# ── Change Password ───────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    current  = request.data.get('current_password')
    new_pass = request.data.get('new_password')
    if not current or not new_pass:
        return Response({'error': 'Both current and new password are required'}, status=status.HTTP_400_BAD_REQUEST)
    if not request.user.check_password(current):
        return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
    if len(new_pass) < 6:
        return Response({'error': 'New password must be at least 6 characters'}, status=status.HTTP_400_BAD_REQUEST)
    request.user.set_password(new_pass)
    request.user.save()
    return Response({'message': 'Password changed successfully'})

# ── Toggle 2FA ────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_2fa(request):
    request.user.two_fa_enabled = not request.user.two_fa_enabled
    request.user.save()
    return Response({
        'message': f"2FA {'enabled' if request.user.two_fa_enabled else 'disabled'} successfully",
        'two_fa_enabled': request.user.two_fa_enabled
    })

# ── Deactivate Account ────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deactivate_account(request):
    password = request.data.get('password')
    if not password:
        return Response({'error': 'Password required to deactivate account'}, status=status.HTTP_400_BAD_REQUEST)
    if not request.user.check_password(password):
        return Response({'error': 'Incorrect password'}, status=status.HTTP_400_BAD_REQUEST)
    request.user.is_active = False
    request.user.save()
    return Response({'message': 'Account deactivated successfully'})

# ── Logout ────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
    except Exception:
        pass
    return Response({'message': 'Logged out successfully'})

# ── Users by role ─────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_by_role(request, role):
    if request.user.role != 'admin':
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    users = User.objects.filter(role=role)
    return Response(UserSerializer(users, many=True, context={'request': request}).data)

# ── Forgot / Reset Password ────────────────────────────────
token_generator = PasswordResetTokenGenerator()
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:5173')
RESEND_API_KEY = config('RESEND_API_KEY', default='')


def send_reset_email(to_email, full_name, reset_link):
    """Send the password reset email via Resend's HTTP API (SMTP is blocked on Render free tier)."""
    response = requests.post(
        'https://api.resend.com/emails',
        headers={
            'Authorization': f'Bearer {RESEND_API_KEY}',
            'Content-Type': 'application/json',
        },
        json={
            'from': 'EduStruc <onboarding@resend.dev>',  # swap to your verified domain sender once set up in Resend
            'to': [to_email],
            'subject': 'Reset your EduStruc password',
            'html': f'''
                <p>Hi {full_name},</p>
                <p>Click the link below to reset your password. This link expires in 1 hour:</p>
                <p><a href="{reset_link}">{reset_link}</a></p>
                <p>If you did not request this, you can safely ignore this email.</p>
            ''',
        },
        timeout=8,
    )
    response.raise_for_status()


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data.get('email', '').strip().lower()

    if not email:
        return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response({'message': 'If that email exists, a reset link has been sent.'})

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)

    if user.role == 'teacher':
        reset_link = f"{FRONTEND_URL}/teacher/reset-password/{uid}/{token}"
    else:
        reset_link = f"{FRONTEND_URL}/reset-password/{uid}/{token}"

    try:
        send_reset_email(user.email, user.full_name, reset_link)
    except Exception as e:
        print('Resend email error:', e)
        return Response(
            {'error': 'Could not send reset email. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response({'message': 'If that email exists, a reset link has been sent.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request, uid, token):
    password = request.data.get('password', '')
    if not password or len(password) < 8:
        return Response({'error': 'Password must be at least 8 characters.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        return Response({'error': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)

    if not token_generator.check_token(user, token):
        return Response({'error': 'This reset link is invalid or has expired.'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(password)
    user.save()

    return Response({'message': 'Password has been reset successfully.'})