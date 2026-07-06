from django.urls import path
from .views import GradeListView, SubjectListView, TeacherListView, TeacherDetailView

urlpatterns = [
    path('',            TeacherListView.as_view(),   name='teacher-list'),
    path('<int:pk>/',   TeacherDetailView.as_view(), name='teacher-detail'),
    path('grades/',     GradeListView.as_view(),     name='grade-list'),
    path('subjects/',   SubjectListView.as_view(),   name='subject-list'),
]