from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Grade
from .serializers import GradeSerializer

class GradeListView(generics.ListCreateAPIView):
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Grade.objects.all()
        student_id = self.request.query_params.get('student')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        return queryset

class GradeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]

class StudentGPAView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, student_id):
        grades = Grade.objects.filter(student_id=student_id)
        if not grades.exists():
            return Response({'gpa': 0, 'total': 0})
        total = sum((g.score / g.max_score) * 100 for g in grades)
        avg = round(total / grades.count(), 1)
        return Response({
            'gpa': avg,
            'total': grades.count(),
            'grade_letter': 'A' if avg >= 90 else 'B+' if avg >= 80 else 'B' if avg >= 70 else 'C'
        })