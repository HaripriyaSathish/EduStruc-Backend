from django.urls import path
from . import views

urlpatterns = [
    path('fees/', views.FeeListView.as_view(), name='fee-list'),
    path('create-order/', views.CreateOrderView.as_view(), name='create-order'),
    path('verify/', views.VerifyPaymentView.as_view(), name='verify-payment'),
    path('history/', views.PaymentHistoryView.as_view(), name='payment-history'),
    path('cards/', views.SavedCardsView.as_view(), name='saved-cards'),
    path('cards/<int:card_id>/', views.DeleteSavedCardView.as_view(), name='delete-card'),
]