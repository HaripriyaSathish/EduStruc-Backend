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