from django.urls import path
from . import views

urlpatterns = [
    path('<int:student_id>/', views.StudentAttendanceView.as_view(), name='student-attendance'),
    path('bulk/', views.BulkAttendanceView.as_view(), name='bulk-attendance'),
    path('bulk/list/', views.BulkAttendanceByClassView.as_view(), name='bulk-attendance-list'),
]