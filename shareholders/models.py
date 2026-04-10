from django.db import models


class Shareholder(models.Model):
    shareholder_code = models.CharField(max_length=100, unique=True)
    shareholder_name = models.CharField(max_length=200)
    mobile_number = models.CharField(max_length=20, db_index=True)
    email = models.EmailField(blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    state = models.CharField(max_length=120, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.shareholder_name} - {self.shareholder_code}"