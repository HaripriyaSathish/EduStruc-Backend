from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Course
from .serializers import CourseSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def course_list(request):
    if request.method == 'GET':
        if request.user.role == 'teacher':
            profile = getattr(request.user, 'teacher_profile', None)
            if profile:
                courses = Course.objects.filter(
                    Q(teacher=profile) | Q(instructor=request.user.full_name)
                ).distinct()
            else:
                courses = Course.objects.filter(instructor=request.user.full_name)
        else:
            courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def course_detail(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(CourseSerializer(course).data)
    elif request.method == 'PUT':
        serializer = CourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        course.delete()
        return Response({'message': 'Course deleted'}, status=status.HTTP_204_NO_CONTENT)
    

import re
from students.models import Student
from students.serializers import StudentSerializer


def _grade_key(name):
    """Normalizes 'Grade 9', '9th Grade', 'Kindergarten 1' to a comparable key."""
    if not name:
        return ''
    name = name.lower()
    m = re.search(r'(\d+)', name)
    if 'kindergarten' in name or 'kg' in name:
        return f'kg{m.group(1)}' if m else 'kg'
    return f'g{m.group(1)}' if m else name.strip()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_students(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    if course.grade:
        target = _grade_key(course.grade.name)
        students = [s for s in Student.objects.all() if _grade_key(s.class_name) == target]
    else:
        # No grade linked to this course yet — show everyone as a fallback
        students = list(Student.objects.all())

    return Response(StudentSerializer(students, many=True).data)    