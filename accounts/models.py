from django.db import models


class ShareholderOtpLog(models.Model):
    PURPOSE_CHOICES = [
        ('LOGIN', 'Login'),
    ]

    mobile_number = models.CharField(max_length=20, db_index=True)
    otp_code = models.CharField(max_length=20)
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES, default='LOGIN')
    is_verified = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(blank=True, null=True)
    ip_address = models.CharField(max_length=100, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.mobile_number
        
from django.contrib.auth.models import Group


class RolePermission(models.Model):
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name='role_permission'
    )

    can_view_requests = models.BooleanField(default=False)
    can_create_request = models.BooleanField(default=False)
    can_accept_request = models.BooleanField(default=False)
    can_reject_request = models.BooleanField(default=False)
    can_ship_request = models.BooleanField(default=False)
    can_deliver_request = models.BooleanField(default=False)

    can_bulk_tracking = models.BooleanField(default=False)
    can_bulk_delivery = models.BooleanField(default=False)
    can_bulk_share_upload = models.BooleanField(default=False)
    can_bulk_share_status = models.BooleanField(default=False)

    can_view_reports = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_manage_roles = models.BooleanField(default=False)
    can_manage_branches = models.BooleanField(default=False)
    can_manage_share_status = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    can_reset_user_password = models.BooleanField(default=False)

    def __str__(self):
        return f"Permissions - {self.group.name}"