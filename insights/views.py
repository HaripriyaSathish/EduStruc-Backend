from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import StudentInsight
from .serializers import StudentInsightSerializer

class StudentInsightView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, student_id):
        try:
            insight = StudentInsight.objects.get(student_id=student_id)
            return Response(StudentInsightSerializer(insight).data)
        except StudentInsight.DoesNotExist:
            return Response({
                'academic_insight': '',
                'performance_strengths': [],
                'class_rank': ''
            })