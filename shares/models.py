from django.db import models
from shareholders.models import Shareholder
from masters.models import Branch


class Share(models.Model):
    GIFT_STATUS_CHOICES = [
        ('ELIGIBLE', 'Eligible'),
        ('STOPPED', 'Stopped'),
    ]

    shareholder = models.ForeignKey(
        Shareholder,
        on_delete=models.CASCADE,
        related_name='shares'
    )
    share_number = models.CharField(max_length=100, unique=True)
    certificate_number = models.CharField(max_length=100, blank=True, null=True)
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name='shares'
    )
    gift_status = models.CharField(
        max_length=20,
        choices=GIFT_STATUS_CHOICES,
        default='ELIGIBLE'
    )
    stop_reason = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.share_number