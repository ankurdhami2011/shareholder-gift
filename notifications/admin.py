from django.contrib import admin
from .models import SmsTemplate, SmsLog


@admin.register(SmsTemplate)
class SmsTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'template_code', 'template_name', 'is_active', 'created_at')
    search_fields = ('template_code', 'template_name')
    list_filter = ('is_active',)


@admin.register(SmsLog)
class SmsLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'mobile_number',
        'template_code',
        'send_status',
        'reference_type',
        'reference_id',
        'sent_at',
        'created_at',
    )
    search_fields = ('mobile_number', 'template_code', 'message_text')
    list_filter = ('send_status', 'template_code', 'reference_type')