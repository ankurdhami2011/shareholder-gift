from django.contrib import admin
from .models import AuditLog, AuditLogDetail


class AuditLogDetailInline(admin.TabularInline):
    model = AuditLogDetail
    extra = 0
    readonly_fields = ('column_name', 'old_value', 'new_value', 'created_at')
    can_delete = False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'module_name',
        'table_name',
        'record_id',
        'action_type',
        'changed_by_type',
        'changed_by_id',
        'branch',
        'created_at',
    )
    list_filter = ('module_name', 'table_name', 'action_type', 'changed_by_type', 'created_at')
    search_fields = ('table_name', 'record_id', 'remarks')
    inlines = [AuditLogDetailInline]


@admin.register(AuditLogDetail)
class AuditLogDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'audit_log', 'column_name', 'old_value', 'new_value', 'created_at')
    search_fields = ('column_name', 'old_value', 'new_value')