from django.db import models
from masters.models import Branch


class AuditLog(models.Model):
    ACTION_TYPE_CHOICES = [
        ('INSERT', 'Insert'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('OTP_SENT', 'OTP Sent'),
        ('OTP_VERIFIED', 'OTP Verified'),
        ('SUBMIT_REQUEST', 'Submit Request'),
        ('ACCEPT_REQUEST', 'Accept Request'),
        ('REJECT_REQUEST', 'Reject Request'),
        ('SHIP_REQUEST', 'Ship Request'),
        ('DELIVER_REQUEST', 'Deliver Request'),
        ('UPLOAD_DOCUMENT', 'Upload Document'),
        ('DOWNLOAD_ACKNOWLEDGEMENT', 'Download Acknowledgement'),
    ]

    CHANGED_BY_TYPE_CHOICES = [
        ('SHAREHOLDER', 'Shareholder'),
        ('STAFF', 'Staff'),
        ('ADMIN', 'Admin'),
        ('SYSTEM', 'System'),
    ]

    module_name = models.CharField(max_length=100)
    table_name = models.CharField(max_length=100)
    record_id = models.BigIntegerField()
    action_type = models.CharField(max_length=30, choices=ACTION_TYPE_CHOICES)
    changed_by_type = models.CharField(max_length=20, choices=CHANGED_BY_TYPE_CHOICES)
    changed_by_id = models.BigIntegerField(blank=True, null=True)
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='audit_logs'
    )
    ip_address = models.CharField(max_length=100, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.table_name} - {self.action_type}"


class AuditLogDetail(models.Model):
    audit_log = models.ForeignKey(
        AuditLog,
        on_delete=models.CASCADE,
        related_name='details'
    )
    column_name = models.CharField(max_length=150)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.column_name