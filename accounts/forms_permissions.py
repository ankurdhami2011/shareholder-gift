from django import forms
from .models import RolePermission


class RolePermissionForm(forms.ModelForm):
    class Meta:
        model = RolePermission
        exclude = ['group', 'created_at', 'updated_at']
        widgets = {
            'can_view_requests': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_create_request': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_accept_request': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_reject_request': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_ship_request': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_deliver_request': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_bulk_tracking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_bulk_delivery': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_bulk_share_upload': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_bulk_share_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_view_reports': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_users': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_roles': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_branches': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_share_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_reset_user_password': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }