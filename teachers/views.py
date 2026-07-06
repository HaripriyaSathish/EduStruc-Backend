from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Grade, Subject, TeacherProfile
from .serializers import GradeSerializer, SubjectSerializer, TeacherListSerializer, TeacherDetailSerializer


class GradeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        grades = Grade.objects.all().order_by('order')
        return Response(GradeSerializer(grades, many=True).data)


class SubjectListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subjects = Subject.objects.all().order_by('name')
        return Response(SubjectSerializer(subjects, many=True).data)


class TeacherListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        teachers = TeacherProfile.objects.select_related('user').all().order_by('user__full_name')
        return Response(TeacherListSerializer(teachers, many=True).data)


class TeacherDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            teacher = TeacherProfile.objects.select_related('user').get(pk=pk)
        except TeacherProfile.DoesNotExist:
            return Response({'detail': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(TeacherDetailSerializer(teacher).data)