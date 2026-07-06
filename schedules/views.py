from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Schedule
from .serializers import ScheduleSerializer


def sync_teacher_timetable(schedule):
    """
    Keeps a TeacherTimetable row in sync with this Schedule entry.
    Only creates/updates a timetable row if teacher, subject, and grade
    are all linked on the schedule. If any are missing, removes any
    previously-synced timetable entry for this schedule.
    """
    from teachers.models import TeacherTimetable

    existing = getattr(schedule, 'timetable_entry', None)

    if not (schedule.teacher and schedule.subject and schedule.grade):
        if existing:
            existing.delete()
        return

    TeacherTimetable.objects.update_or_create(
        source_schedule=schedule,
        defaults={
            'teacher':    schedule.teacher,
            'subject':    schedule.subject,
            'grade':      schedule.grade,
            'day':        schedule.day,
            'start_time': schedule.start_time,
            'end_time':   schedule.end_time,
            'room':       schedule.room,
        }
    )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def schedule_list(request):
    if request.method == 'GET':
        if request.user.role == 'teacher':
            profile = getattr(request.user, 'teacher_profile', None)
            if profile:
                schedules = Schedule.objects.filter(
                    Q(teacher=profile) | Q(instructor=request.user.full_name)
                ).distinct()
            else:
                schedules = Schedule.objects.filter(instructor=request.user.full_name)
        else:
            schedules = Schedule.objects.all()
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ScheduleSerializer(data=request.data)
        if serializer.is_valid():
            schedule = serializer.save()
            sync_teacher_timetable(schedule)
            return Response(ScheduleSerializer(schedule).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def schedule_detail(request, pk):
    try:
        schedule = Schedule.objects.get(pk=pk)
    except Schedule.DoesNotExist:
        return Response({'error': 'Schedule not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(ScheduleSerializer(schedule).data)
    elif request.method == 'PUT':
        serializer = ScheduleSerializer(schedule, data=request.data, partial=True)
        if serializer.is_valid():
            schedule = serializer.save()
            sync_teacher_timetable(schedule)
            return Response(ScheduleSerializer(schedule).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        schedule.delete()  # CASCADE on source_schedule cleans up the synced timetable row
        return Response({'message': 'Schedule deleted'}, status=status.HTTP_204_NO_CONTENT)