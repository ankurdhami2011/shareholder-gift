from django.contrib import admin
from .models import StaffUser, StaffBranchAccess

admin.site.register(StaffUser)
admin.site.register(StaffBranchAccess)