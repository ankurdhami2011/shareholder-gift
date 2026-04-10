from django.urls import path
from .views import shareholder_share_list, share_delivery_profile

urlpatterns = [
    path('', shareholder_share_list, name='share-list'),
    path('<int:share_id>/delivery-profile/', share_delivery_profile, name='share-delivery-profile'),
]