# support_tickets/urls.py  (create this new file)
 
from django.urls import path
from . import views
 
urlpatterns = [
    path('',               views.ticket_list,     name='ticket-list'),
    path('<int:pk>/',      views.ticket_detail,   name='ticket-detail'),
    path('<int:pk>/respond/', views.respond_ticket, name='ticket-respond'),
    path('<int:pk>/resolve/', views.resolve_ticket, name='ticket-resolve'),
]
 