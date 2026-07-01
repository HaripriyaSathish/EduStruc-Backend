from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import Attendance
from .serializers import AttendanceSerializer
from datetime import date

class StudentAttendanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, student_id):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        queryset = Attendance.objects.filter(student_id=student_id)
        
        if month and year:
            queryset = queryset.filter(
                date__month=month,
                date__year=year
            )
        
        serializer = AttendanceSerializer(queryset, many=True)
        
        # Calculate stats
        total = queryset.count()
        present = queryset.filter(status='present').count()
        absent = queryset.filter(status='absent').count()
        holiday = queryset.filter(status='holiday').count()
        score = round((present / total) * 100) if total > 0 else 0
        missed = absent
        
        return Response({
            'records': serializer.data,
            'stats': {
                'total': total,
                'present': present,
                'absent': absent,
                'holiday': holiday,
                'score': score,
                'missed': missed,
            }
        })
    
# ADD this to attendance/views.py



from rest_framework import status
from django.utils import timezone

from students.models import Student


class BulkAttendanceView(APIView):
    """
    POST /api/attendance/bulk/
    
    Body:
    {
        "date": "2024-06-30",
        "event_name": "Regular School Day",
        "records": [
            {"student": 1, "status": "present"},
            {"student": 2, "status": "absent"},
            {"student": 3, "status": "holiday"},
            ...500 students in one call...
        ]
    }
    
    Saves all 500 attendance records in a single request.
    Uses update_or_create so re-submitting the same date updates instead of duplicating.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        date       = request.data.get('date')
        event_name = request.data.get('event_name', 'Regular School Day')
        event_type = request.data.get('event_type', 'Standard Attendance')
        records    = request.data.get('records', [])

        if not date:
            return Response({'error': 'date is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not records:
            return Response({'error': 'records list is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        created_count = 0
        updated_count = 0
        errors        = []

        for record in records:
            student_id    = record.get('student')
            att_status    = record.get('status', 'present')
            notes         = record.get('notes', '')

            if not student_id:
                errors.append({'record': record, 'error': 'student id missing'})
                continue

            obj, created = Attendance.objects.update_or_create(
                student_id=student_id,
                date=date,
                defaults={
                    'status':     att_status,
                    'event_name': event_name,
                    'event_type': event_type,
                    'notes':      notes,
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        return Response({
            'success':  True,
            'created':  created_count,
            'updated':  updated_count,
            'errors':   errors,
            'date':     date,
            'total':    len(records),
        })


class BulkAttendanceByClassView(APIView):
    """
    GET /api/attendance/bulk/?date=2024-06-30&class_name=10th+Grade
    
    Returns all students in the class with their attendance status for that date,
    ready to display in the Teacher's bulk attendance form.
    If no attendance record exists for a student on that date,
    returns status='upcoming' so the teacher can mark it.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        date       = request.query_params.get('date', timezone.now().date().isoformat())
        class_name = request.query_params.get('class_name')
        course_id  = request.query_params.get('course')

        students = Student.objects.all()
        if class_name:
            students = students.filter(class_name=class_name)

        result = []
        attendance_map = {
            a.student_id: a
            for a in Attendance.objects.filter(
                student__in=students,
                date=date
            )
        }

        for student in students:
            att = attendance_map.get(student.id)
            result.append({
                'student_id':   student.id,
                'full_name':    student.full_name,
                'roll_number':  student.roll_number,
                'class_name':   student.class_name,
                'status':       att.status if att else 'upcoming',
                'notes':        att.notes if att else '',
                'attendance_id': att.id if att else None,
            })

        return Response({
            'date':     date,
            'students': result,
            'total':    len(result),
        })    
