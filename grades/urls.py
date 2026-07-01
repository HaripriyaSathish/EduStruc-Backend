from django.urls import path
from . import views

urlpatterns = [
    path('', views.GradeListView.as_view(), name='grade-list'),
    path('<int:pk>/', views.GradeDetailView.as_view(), name='grade-detail'),
    path('gpa/<int:student_id>/', views.StudentGPAView.as_view(), name='student-gpa'),
]