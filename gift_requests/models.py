from django.db import models
from shareholders.models import Shareholder
from shares.models import Share
from masters.models import Branch, GiftCycle


class GiftRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
    ]

    CREATED_BY_TYPE_CHOICES = [
        ('SHAREHOLDER', 'Shareholder'),
        ('STAFF', 'Staff'),
        ('ADMIN', 'Admin'),
        ('SYSTEM', 'System'),
    ]

    request_no = models.CharField(max_length=100, unique=True)
    shareholder = models.ForeignKey(
        Shareholder,
        on_delete=models.PROTECT,
        related_name='gift_requests'
    )
    share = models.ForeignKey(
        Share,
        on_delete=models.PROTECT,
        related_name='gift_requests'
    )
    gift_cycle = models.ForeignKey(
        GiftCycle,
        on_delete=models.PROTECT,
        related_name='gift_requests'
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name='gift_requests'
    )

    mobile_number = models.CharField(max_length=20)

    request_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    rejection_reason = models.TextField(blank=True, null=True)

    courier_name = models.CharField(max_length=150, blank=True, null=True)
    tracking_number = models.CharField(max_length=150, blank=True, null=True)

    acknowledgement_file_path = models.TextField(blank=True, null=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    rejected_at = models.DateTimeField(blank=True, null=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    created_by_type = models.CharField(
        max_length=20,
        choices=CREATED_BY_TYPE_CHOICES,
        default='SHAREHOLDER'
    )
    created_by_id = models.BigIntegerField(blank=True, null=True)
    updated_by_type = models.CharField(
        max_length=20,
        choices=CREATED_BY_TYPE_CHOICES,
        blank=True,
        null=True
    )
    updated_by_id = models.BigIntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['request_no']),
            models.Index(fields=['mobile_number']),
            models.Index(fields=['request_status']),
            models.Index(fields=['branch']),
            models.Index(fields=['gift_cycle']),
        ]

    def __str__(self):
        return self.request_no


class RequestDeliveryAddress(models.Model):
    gift_request = models.OneToOneField(
        GiftRequest,
        on_delete=models.CASCADE,
        related_name='delivery_address'
    )
    recipient_name = models.CharField(max_length=200, blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    pincode = models.CharField(max_length=20)
    is_from_master_address = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Address for {self.gift_request.request_no}"


class GiftRequestDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('SHARE_CERTIFICATE', 'Share Certificate'),
    ]

    gift_request = models.ForeignKey(
        GiftRequest,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    original_file_name = models.CharField(max_length=255)
    stored_file_name = models.CharField(max_length=255)
    file_path = models.TextField()
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_type} - {self.gift_request.request_no}"


class GiftRequestStatusHistory(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
    ]

    CHANGED_BY_TYPE_CHOICES = [
        ('SHAREHOLDER', 'Shareholder'),
        ('STAFF', 'Staff'),
        ('ADMIN', 'Admin'),
        ('SYSTEM', 'System'),
    ]

    gift_request = models.ForeignKey(
        GiftRequest,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    old_status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, null=True)
    new_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    changed_by_type = models.CharField(max_length=20, choices=CHANGED_BY_TYPE_CHOICES)
    changed_by_id = models.BigIntegerField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.gift_request.request_no} - {self.new_status}"