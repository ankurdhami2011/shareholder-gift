from django.urls import path
from . import views
from .views import (
    create_gift_request,
    my_gift_requests,
    my_gift_request_detail,
    download_acknowledgement,
)

urlpatterns = [
    path('', create_gift_request, name='create-gift-request'),
    path('my-requests/', my_gift_requests, name='my-gift-requests'),
    path('my-requests/<int:gift_request_id>/', my_gift_request_detail, name='my-gift-request-detail'),
    path('my-requests/<int:gift_request_id>/acknowledgement/', download_acknowledgement, name='download-acknowledgement'),
    path('staff/requests/', views.staff_request_list, name='staff-web-request-list'),
    path('staff/request/<int:pk>/accept/', views.accept_request, name='accept-request'),
    path('staff/request/<int:pk>/reject/', views.reject_request, name='reject-request'),
    path('staff/request/<int:pk>/tracking/', views.create_tracking, name='create-tracking'),
    path('staff/request/<int:pk>/deliver/', views.mark_delivered, name='mark-delivered'),
]