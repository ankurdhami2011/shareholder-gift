from django.contrib import admin
from .models import GiftRequest, RequestDeliveryAddress, GiftRequestDocument, GiftRequestStatusHistory

admin.site.register(GiftRequest)
admin.site.register(RequestDeliveryAddress)
admin.site.register(GiftRequestDocument)
admin.site.register(GiftRequestStatusHistory)