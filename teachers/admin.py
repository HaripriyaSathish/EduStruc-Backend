from django.contrib import admin
from .models import Grade, Subject, TeacherProfile, TeacherSubjectGrade, TeacherAttendance, TeacherTimetable

admin.site.register(Grade)
admin.site.register(Subject)
admin.site.register(TeacherProfile)
admin.site.register(TeacherSubjectGrade)
admin.site.register(TeacherAttendance)
admin.site.register(TeacherTimetable)