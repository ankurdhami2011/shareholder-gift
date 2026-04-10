from django.db import models


class Branch(models.Model):
    branch_code = models.CharField(max_length=50, unique=True)
    branch_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.branch_name} ({self.branch_code})"


class GiftCycle(models.Model):
    cycle_code = models.CharField(max_length=50, unique=True)
    cycle_name = models.CharField(max_length=150)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cycle_name