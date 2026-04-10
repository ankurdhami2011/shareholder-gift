from django.db import models


class SmsTemplate(models.Model):
    template_code = models.CharField(max_length=100, unique=True)
    template_name = models.CharField(max_length=150)
    message_body = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.template_code


class SmsLog(models.Model):
    SEND_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    ]

    mobile_number = models.CharField(max_length=20)
    template_code = models.CharField(max_length=100, blank=True, null=True)
    message_text = models.TextField()
    send_status = models.CharField(max_length=20, choices=SEND_STATUS_CHOICES, default='PENDING')
    provider_response = models.TextField(blank=True, null=True)
    reference_type = models.CharField(max_length=50, blank=True, null=True)
    reference_id = models.BigIntegerField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.mobile_number} - {self.send_status}"