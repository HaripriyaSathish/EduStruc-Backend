from django.urls import path
from . import views

urlpatterns = [
    path('', views.AnnouncementListView.as_view(), name='announcement-list'),
    path('<int:pk>/', views.AnnouncementDetailView.as_view(), name='announcement-detail'),
]