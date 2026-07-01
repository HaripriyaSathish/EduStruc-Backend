from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import Message
from .serializers import MessageSerializer

class InboxView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        archived = request.query_params.get('archived', 'false') == 'true'
        search = request.query_params.get('search', '')
        messages = Message.objects.filter(
            recipient=request.user,
            is_archived=archived
        )
        if search:
            messages = messages.filter(subject__icontains=search) | \
                      messages.filter(sender_name__icontains=search) | \
                      messages.filter(body__icontains=search)
        return Response(MessageSerializer(messages, many=True).data)

class MessageDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            msg = Message.objects.get(pk=pk, recipient=request.user)
            msg.is_read = True
            msg.save()
            return Response(MessageSerializer(msg).data)
        except Message.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            msg = Message.objects.get(pk=pk, recipient=request.user)
            msg.delete()
            return Response({'message': 'Deleted'})
        except Message.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

class ArchiveMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            msg = Message.objects.get(pk=pk, recipient=request.user)
            msg.is_archived = True
            msg.save()
            return Response({'message': 'Archived'})
        except Message.DoesNotExist:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

class UnreadCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Message.objects.filter(
            recipient=request.user,
            is_read=False,
            is_archived=False
        ).count()
        return Response({'unread': count})