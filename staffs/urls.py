from django.urls import path
from .views import (
    staff_login,
    staff_gift_request_list,
    accept_gift_request,
    reject_gift_request,
    ship_gift_request,
    deliver_gift_request,
)

urlpatterns = [
    path('login/', staff_login, name='staff-login'),
    path('gift-requests/', staff_gift_request_list, name='staff-gift-request-list'),
    path('gift-requests/<int:gift_request_id>/accept/', accept_gift_request, name='accept-gift-request'),
    path('gift-requests/<int:gift_request_id>/reject/', reject_gift_request, name='reject-gift-request'),
    path('gift-requests/<int:gift_request_id>/ship/', ship_gift_request, name='ship-gift-request'),
    path('gift-requests/<int:gift_request_id>/deliver/', deliver_gift_request, name='deliver-gift-request'),
]