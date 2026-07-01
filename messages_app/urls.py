from django.urls import path
from . import views

urlpatterns = [
    path('', views.InboxView.as_view(), name='inbox'),
    path('<int:pk>/', views.MessageDetailView.as_view(), name='message-detail'),
    path('<int:pk>/archive/', views.ArchiveMessageView.as_view(), name='archive-message'),
    path('unread/', views.UnreadCountView.as_view(), name='unread-count'),
]