from rest_framework import status,generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

class MyChildrenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        children = Student.objects.filter(parent=request.user)
        serializer = StudentSerializer(children, many=True, context={'request': request})
        return Response(serializer.data)

# students/views.py (or wherever StudentViewSet/StudentCreateView is)
# ADD this view for avatar upload — PATCH /api/students/:id/avatar/

from rest_framework.decorators import action

from rest_framework import  status
from rest_framework.parsers import MultiPartParser, FormParser

# If you use a ViewSet, add this action inside it:
@action(detail=True, methods=['patch'], parser_classes=[MultiPartParser, FormParser])
def upload_avatar(self, request, pk=None):
    student = self.get_object()
    if 'avatar' not in request.FILES:
        return Response({'error': 'No avatar file provided.'}, status=status.HTTP_400_BAD_REQUEST)
    student.avatar = request.FILES['avatar']
    student.save()
    avatar_url = request.build_absolute_uri(student.avatar.url) if student.avatar else None
    return Response({'avatar_url': avatar_url})

# If you use generic views (ListCreateAPIView etc.), add a separate view:
class StudentAvatarView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, pk):
        from students.models import Student
        student = Student.objects.get(pk=pk)
        if 'avatar' not in request.FILES:
            return Response({'error': 'No file.'}, status=400)
        student.avatar = request.FILES['avatar']
        student.save()
        url = request.build_absolute_uri(student.avatar.url) if student.avatar else None
        return Response({'avatar_url': url})