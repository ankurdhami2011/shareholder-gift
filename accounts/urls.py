from django.urls import path
from . import views

urlpatterns = [
    path('send-otp/', views.send_otp, name='send-otp'),
    path('verify-otp/', views.verify_otp, name='verify-otp'),
    path('my-profile/', views.my_profile, name='my-profile'),

    path('roles/', views.role_list, name='role_list'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/permissions/', views.role_permission_list, name='role_permission_list'),
    path('roles/<int:group_id>/permissions/', views.role_permission_edit, name='role_permission_edit'),

    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/reset-password/', views.user_reset_password, name='user_reset_password'),
]