from django.db import models
from masters.models import Branch


class StaffUser(models.Model):
    ROLE_CHOICES = [
        ('BRANCH_STAFF', 'Branch Staff'),
        ('MULTI_BRANCH_STAFF', 'Multi Branch Staff'),
        ('MASTER_STAFF', 'Master Staff'),
        ('ADMIN', 'Admin'),
    ]

    staff_code = models.CharField(max_length=100, unique=True)
    full_name = models.CharField(max_length=200)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    username = models.CharField(max_length=100, unique=True)
    password_hash = models.TextField()
    role_type = models.CharField(max_length=30, choices=ROLE_CHOICES)
    has_all_branch_access = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class StaffBranchAccess(models.Model):
    staff_user = models.ForeignKey(
        StaffUser,
        on_delete=models.CASCADE,
        related_name='branch_accesses'
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='staff_accesses'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('staff_user', 'branch')

    def __str__(self):
        return f"{self.staff_user.full_name} - {self.branch.branch_name}"