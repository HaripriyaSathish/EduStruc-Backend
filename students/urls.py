from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student-list'),
    path('stats/', views.dashboard_stats, name='dashboard-stats'),
    path('my-children/', views.MyChildrenView.as_view(), name='my-children'),
    path('<int:pk>/avatar/', views.StudentAvatarView.as_view(), name='student-avatar'),
    path('<int:pk>/', views.student_detail, name='student-detail'),
]