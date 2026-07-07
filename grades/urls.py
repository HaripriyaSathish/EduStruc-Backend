from django.urls import path
from .views import GradeListView, GradeDetailView, StudentGPAView, BulkGradeSaveView

urlpatterns = [
    path('', GradeListView.as_view(), name='grade-list'),
    path('bulk/', BulkGradeSaveView.as_view(), name='grade-bulk'),
    path('gpa/<int:student_id>/', StudentGPAView.as_view(), name='student-gpa'),
    path('<int:pk>/', GradeDetailView.as_view(), name='grade-detail'),
]