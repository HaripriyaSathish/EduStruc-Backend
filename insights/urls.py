from django.urls import path
from . import views

urlpatterns = [
    path('<int:student_id>/', views.StudentInsightView.as_view(), name='student-insight'),
]