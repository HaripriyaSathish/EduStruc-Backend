from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Grade
from .serializers import GradeSerializer


class GradeListView(generics.ListCreateAPIView):
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Grade.objects.all()
        student_id = self.request.query_params.get('student')
        course_id  = self.request.query_params.get('course')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
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


class BulkGradeSaveView(APIView):
    """
    POST /api/grades/bulk/
    Body: {
      "course": 5,
      "assessment_name": "Midterm Exam",
      "assessment_type": "Exam",
      "date": "2026-07-07",
      "records": [{"student": 1, "score": 85}, {"student": 2, "score": 70}, ...]
    }
    update_or_create per student+course+assessment_name, so re-saving the
    same assessment updates instead of duplicating rows.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        course_id       = request.data.get('course')
        assessment_name = request.data.get('assessment_name', 'Overall Score')
        assessment_type = request.data.get('assessment_type', 'Overall')
        date            = request.data.get('date') or timezone.now().date().isoformat()
        records         = request.data.get('records', [])

        if not course_id:
            return Response({'error': 'course is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not records:
            return Response({'error': 'records list is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        saved = []
        for record in records:
            student_id = record.get('student')
            score      = record.get('score')
            if student_id is None or score is None:
                continue
            grade, _ = Grade.objects.update_or_create(
                student_id=student_id,
                course_id=course_id,
                assessment_name=assessment_name,
                defaults={
                    'score': score,
                    'max_score': 100,
                    'assessment_type': assessment_type,
                    'date': date,
                }
            )
            saved.append(grade.id)

        return Response({'success': True, 'saved_count': len(saved)})