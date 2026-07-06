import base64

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Student
from .serializers import StudentSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def student_list(request):
    if request.method == 'GET':
        search   = request.query_params.get('search', '')
        students = Student.objects.filter(full_name__icontains=search) if search else Student.objects.all()
        return Response(StudentSerializer(students, many=True).data)
    serializer = StudentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def student_detail(request, pk):
    try:
        student = Student.objects.get(pk=pk)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(StudentSerializer(student).data)
    elif request.method == 'PUT':
        serializer = StudentSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        student.delete()
        return Response({'message': 'Student deleted'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    from courses.models import Course
    from schedules.models import Schedule
    from users.models import User
    from attendance.models import Attendance

    total_students   = Student.objects.count()
    active_courses   = Course.objects.filter(status='active').count()
    active_schedules = Schedule.objects.count()
    faculty_members  = User.objects.filter(role='teacher').count()

    # Average attendance = present records / (present + absent records) * 100
    # Holiday and Upcoming records are excluded since they aren't a student
    # actually showing up or not — they're not real attendance outcomes yet.
    countable_records = Attendance.objects.filter(status__in=['present', 'absent'])
    total_countable    = countable_records.count()
    present_count      = countable_records.filter(status='present').count()

    attendance_pct = round((present_count / total_countable) * 100) if total_countable > 0 else 0

    return Response({
        'total_students':   total_students,
        'active_courses':   active_courses,
        'active_schedules': active_schedules,
        'faculty_members':  faculty_members,
        'attendance':       attendance_pct,
    })


class MyChildrenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        children = Student.objects.filter(parent=request.user)
        serializer = StudentSerializer(children, many=True, context={'request': request})
        return Response(serializer.data)


# students/views.py
# PATCH or POST /api/students/:id/avatar/
# Stores the uploaded avatar as base64 (avatar_base64 field) since Render's
# filesystem is ephemeral and file-based uploads get wiped on redeploy/restart.
class StudentAvatarView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        return self._handle_upload(request, pk)

    def patch(self, request, pk):
        return self._handle_upload(request, pk)

    def _handle_upload(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        if 'avatar' not in request.FILES:
            return Response({'error': 'No avatar file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        avatar_file = request.FILES['avatar']
        content_type = avatar_file.content_type or 'image/jpeg'
        encoded = base64.b64encode(avatar_file.read()).decode('utf-8')
        student.avatar_base64 = f'data:{content_type};base64,{encoded}'
        student.save()

        return Response({'avatar_url': student.avatar_base64})