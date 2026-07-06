from rest_framework import serializers
from .models import Grade, Subject, TeacherProfile, TeacherSubjectGrade, TeacherAttendance, TeacherTimetable


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'name', 'order']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']


class TeacherSubjectGradeSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    grade_name   = serializers.CharField(source='grade.name', read_only=True)

    class Meta:
        model = TeacherSubjectGrade
        fields = ['id', 'subject', 'subject_name', 'grade', 'grade_name']


class TeacherListSerializer(serializers.ModelSerializer):
    full_name      = serializers.CharField(source='user.full_name', read_only=True)
    email          = serializers.CharField(source='user.email', read_only=True)
    phone          = serializers.CharField(source='user.phone', read_only=True)
    avatar_base64  = serializers.CharField(source='user.avatar_base64', read_only=True)
    subjects_count = serializers.SerializerMethodField()
    grades_handled = serializers.SerializerMethodField()

    class Meta:
        model = TeacherProfile
        fields = [
            'id', 'full_name', 'email', 'phone', 'avatar_base64',
            'employee_id', 'department', 'designation',
            'subjects_count', 'grades_handled',
        ]

    def get_subjects_count(self, obj):
        return obj.subject_grades.values('subject').distinct().count()

    def get_grades_handled(self, obj):
        return list(obj.subject_grades.values_list('grade__name', flat=True).distinct())


class TeacherAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherAttendance
        fields = ['id', 'date', 'status', 'notes']


class TeacherTimetableSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    grade_name   = serializers.CharField(source='grade.name', read_only=True)

    class Meta:
        model = TeacherTimetable
        fields = ['id', 'day', 'start_time', 'end_time', 'room', 'subject', 'subject_name', 'grade', 'grade_name']


class TeacherDetailSerializer(serializers.ModelSerializer):
    full_name           = serializers.CharField(source='user.full_name', read_only=True)
    email               = serializers.CharField(source='user.email', read_only=True)
    phone               = serializers.CharField(source='user.phone', read_only=True)
    avatar_base64       = serializers.CharField(source='user.avatar_base64', read_only=True)
    subject_grades      = TeacherSubjectGradeSerializer(many=True, read_only=True)
    timetable           = serializers.SerializerMethodField()
    attendance_summary  = serializers.SerializerMethodField()
    attendance_records  = serializers.SerializerMethodField()

    class Meta:
        model = TeacherProfile
        fields = [
            'id', 'full_name', 'email', 'phone', 'avatar_base64',
            'employee_id', 'department', 'designation', 'date_joined',
            'subject_grades', 'timetable', 'attendance_summary', 'attendance_records',
        ]

    def get_timetable(self, obj):
        qs = obj.timetable.all().order_by('day', 'start_time')
        return TeacherTimetableSerializer(qs, many=True).data

    def get_attendance_records(self, obj):
        qs = obj.attendance.all().order_by('-date')[:30]
        return TeacherAttendanceSerializer(qs, many=True).data

    def get_attendance_summary(self, obj):
        qs = obj.attendance.all()
        total   = qs.count()
        present = qs.filter(status='present').count()
        pct     = round((present / total) * 100, 1) if total else 0
        return {'total_days': total, 'present_days': present, 'attendance_percentage': pct}