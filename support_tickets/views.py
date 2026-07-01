# support_tickets/views.py

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import SupportTicket
from .serializers import SupportTicketSerializer


# ── List + Create ────────────────────────────────────────────
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def ticket_list(request):
    if request.method == 'GET':
        # Admins see every ticket raised by anyone; everyone else sees only their own.
        if request.user.role == 'admin':
            tickets = SupportTicket.objects.all()
        else:
            tickets = SupportTicket.objects.filter(raised_by=request.user)
        return Response(SupportTicketSerializer(tickets, many=True).data)

    # POST — create a new ticket, always tied to the logged-in user
    subject = request.data.get('subject', '').strip()
    message = request.data.get('message', '').strip()
    if not subject or not message:
        return Response({'error': 'Subject and message are required.'}, status=status.HTTP_400_BAD_REQUEST)

    ticket = SupportTicket.objects.create(
        raised_by = request.user,
        subject   = subject,
        category  = request.data.get('category', 'Technical Issue'),
        priority  = request.data.get('priority', 'Medium'),
        message   = message,
    )
    return Response(SupportTicketSerializer(ticket).data, status=status.HTTP_201_CREATED)


# ── Single ticket detail ─────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ticket_detail(request, pk):
    try:
        ticket = SupportTicket.objects.get(pk=pk)
    except SupportTicket.DoesNotExist:
        return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)

    # Non-admins may only view their own ticket
    if request.user.role != 'admin' and ticket.raised_by_id != request.user.id:
        return Response({'error': 'Not authorized to view this ticket'}, status=status.HTTP_403_FORBIDDEN)

    return Response(SupportTicketSerializer(ticket).data)


# ── Admin responds to a ticket ───────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_ticket(request, pk):
    if request.user.role != 'admin':
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        ticket = SupportTicket.objects.get(pk=pk)
    except SupportTicket.DoesNotExist:
        return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)

    response_text = request.data.get('response', '').strip()
    if not response_text:
        return Response({'error': 'Response message is required.'}, status=status.HTTP_400_BAD_REQUEST)

    ticket.admin_response = response_text
    ticket.responded_by   = request.user
    ticket.status         = 'in_progress'
    ticket.save()

    # Notify the person who raised the ticket, if the notifications app is installed
    try:
        from notifications.models import Notification
        Notification.objects.create(
            user    = ticket.raised_by,
            title   = f'Response to your ticket: {ticket.subject}',
            message = response_text[:200],
            type    = 'system',
            link    = '/support',
        )
    except Exception:
        pass

    return Response(SupportTicketSerializer(ticket).data)


# ── Admin marks a ticket resolved ────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resolve_ticket(request, pk):
    if request.user.role != 'admin':
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)

    try:
        ticket = SupportTicket.objects.get(pk=pk)
    except SupportTicket.DoesNotExist:
        return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)

    ticket.status      = 'resolved'
    ticket.resolved_at = timezone.now()
    ticket.save()

    try:
        from notifications.models import Notification
        Notification.objects.create(
            user    = ticket.raised_by,
            title   = f'Ticket resolved: {ticket.subject}',
            message = 'Your support ticket has been marked as resolved.',
            type    = 'system',
            link    = '/support',
        )
    except Exception:
        pass

    return Response(SupportTicketSerializer(ticket).data)
