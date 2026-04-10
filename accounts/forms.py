from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm

from masters.models import Branch
from staffs.models import StaffUser, StaffBranchAccess


class RoleForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter role name'
            })
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip().upper()
        qs = Group.objects.filter(name__iexact=name)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("Role already exists.")
        return name


ROLE_TYPE_CHOICES = [
    ('BRANCH_STAFF', 'Branch Staff'),
    ('MULTI_BRANCH_STAFF', 'Multi Branch Staff'),
    ('MASTER_STAFF', 'Master Staff'),
    ('ADMIN', 'Admin'),
]


class UserCreateForm(UserCreationForm):
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(required=False, initial=True)
    group = forms.ModelChoiceField(
        queryset=Group.objects.all().order_by('name'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    staff_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    mobile_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    role_type = forms.ChoiceField(
        choices=ROLE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    has_all_branch_access = forms.BooleanField(required=False)
    branches = forms.ModelMultipleChoiceField(
        queryset=Branch.objects.filter(is_active=True).order_by('branch_name'),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'password1', 'password2', 'is_active', 'group',
            'staff_code', 'mobile_number', 'role_type',
            'has_all_branch_access', 'branches'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        has_all_branch_access = cleaned_data.get('has_all_branch_access')
        branches = cleaned_data.get('branches')
        username = cleaned_data.get('username')
        staff_code = cleaned_data.get('staff_code')

        if not has_all_branch_access and not branches:
            self.add_error('branches', 'Select at least one branch or enable all branch access.')

        if username and username.startswith('sh_'):
            self.add_error('username', 'Username starting with sh_ is reserved for shareholder login.')

        if staff_code:
            qs = StaffUser.objects.filter(staff_code__iexact=staff_code.strip())
            if qs.exists():
                self.add_error('staff_code', 'Staff code already exists.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email', '')
        user.is_active = self.cleaned_data.get('is_active', True)

        if commit:
            user.save()
            user.groups.clear()
            selected_group = self.cleaned_data.get('group')
            if selected_group:
                user.groups.add(selected_group)

        return user


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(required=False)
    group = forms.ModelChoiceField(
        queryset=Group.objects.all().order_by('name'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    staff_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    mobile_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    role_type = forms.ChoiceField(
        choices=ROLE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    has_all_branch_access = forms.BooleanField(required=False)
    branches = forms.ModelMultipleChoiceField(
        queryset=Branch.objects.filter(is_active=True).order_by('branch_name'),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'is_active', 'group',
            'staff_code', 'mobile_number', 'role_type',
            'has_all_branch_access', 'branches'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        group = self.instance.groups.first() if self.instance.pk else None
        self.fields['group'].initial = group

        if self.instance.pk:
            staff_user = StaffUser.objects.filter(username=self.instance.username).first()
            if staff_user:
                self.fields['staff_code'].initial = staff_user.staff_code
                self.fields['mobile_number'].initial = staff_user.mobile_number
                self.fields['role_type'].initial = staff_user.role_type
                self.fields['has_all_branch_access'].initial = staff_user.has_all_branch_access
                self.fields['branches'].initial = staff_user.branch_accesses.values_list('branch_id', flat=True)

    def clean(self):
        cleaned_data = super().clean()
        has_all_branch_access = cleaned_data.get('has_all_branch_access')
        branches = cleaned_data.get('branches')
        username = cleaned_data.get('username')
        staff_code = cleaned_data.get('staff_code')

        if not has_all_branch_access and not branches:
            self.add_error('branches', 'Select at least one branch or enable all branch access.')

        if username and username.startswith('sh_'):
            self.add_error('username', 'Username starting with sh_ is reserved for shareholder login.')

        if staff_code:
            qs = StaffUser.objects.filter(staff_code__iexact=staff_code.strip())
            if self.instance.pk:
                qs = qs.exclude(username=self.instance.username)
            if qs.exists():
                self.add_error('staff_code', 'Staff code already exists.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()
            user.groups.clear()
            selected_group = self.cleaned_data.get('group')
            if selected_group:
                user.groups.add(selected_group)

        return user
        
from django.contrib.auth.password_validation import validate_password


class AdminResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        self.target_user = kwargs.pop('target_user', None)
        super().__init__(*args, **kwargs)

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        if self.target_user:
            validate_password(password, self.target_user)
        else:
            validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')

        return cleaned_data