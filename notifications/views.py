# notifications/views.py

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


# ── List current user's notifications (most recent first) ──
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_notifications(request):
    notifications = Notification.objects.filter(user=request.user)[:30]
    unread_count  = Notification.objects.filter(user=request.user, is_read=False).count()
    return Response({
        'results':      NotificationSerializer(notifications, many=True).data,
        'unread_count': unread_count,
    })


# ── Mark a single notification as read ──────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_read(request, pk):
    try:
        notif = Notification.objects.get(pk=pk, user=request.user)
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    notif.is_read = True
    notif.save()
    return Response({'message': 'Marked as read'})


# ── Mark all as read ─────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response({'message': 'All notifications marked as read'})