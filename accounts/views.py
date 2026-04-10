import random
from datetime import timedelta

from django.utils import timezone
from notifications.utils import send_login_otp_sms
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from staffs.models import StaffUser
from django.contrib.auth.hashers import make_password
from shareholders.models import Shareholder
from .models import RolePermission
from .forms_permissions import RolePermissionForm
from .models import ShareholderOtpLog
from .serializers import SendOtpSerializer, VerifyOtpSerializer
from functools import wraps
from staffs.models import StaffUser, StaffBranchAccess
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from .permission_utils import user_has_role_permission
from .forms import RoleForm, UserCreateForm, UserUpdateForm, AdminResetPasswordForm

from staffs.models import StaffUser

def group_required(*group_names):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if request.user.groups.filter(name__in=group_names).exists():
                return view_func(request, *args, **kwargs)

            raise PermissionDenied
        return wrapper
    return decorator


@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    serializer = SendOtpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    mobile_number = serializer.validated_data['mobile_number']

    shareholder_exists = Shareholder.objects.filter(
        mobile_number=mobile_number,
        is_active=True
    ).exists()

    if not shareholder_exists:
        return Response({
            'success': False,
            'message': 'Mobile number not registered',
            'data': None,
            'errors': None
        }, status=status.HTTP_400_BAD_REQUEST)

    otp = str(random.randint(100000, 999999))

    ShareholderOtpLog.objects.create(
        mobile_number=mobile_number,
        otp_code=otp,
        purpose='LOGIN',
        is_verified=False,
        expires_at=timezone.now() + timedelta(minutes=5),
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    sms_result = send_login_otp_sms(mobile_number, otp)

    if not sms_result.get('success'):
        return Response({
            'success': False,
            'message': sms_result.get('message', 'Failed to send OTP SMS'),
            'data': None,
            'errors': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'success': True,
        'message': 'OTP sent successfully',
        'data': {
            'mobile_number': mobile_number,
            'expires_in_seconds': 300
        },
        'errors': None
    }, status=status.HTTP_200_OK)

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from shareholders.models import Shareholder
@login_required
@group_required('ADMIN')
def role_permission_list(request):
    roles = Group.objects.all().order_by('name')
    return render(request, 'accounts/role_permission_list.html', {
        'roles': roles
    })


@login_required
@group_required('ADMIN')
def role_permission_edit(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    permission_obj, _ = RolePermission.objects.get_or_create(group=group)

    if request.method == 'POST':
        form = RolePermissionForm(request.POST, instance=permission_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Permissions updated for {group.name}.')
            return redirect('role_permission_list')
    else:
        form = RolePermissionForm(instance=permission_obj)

    return render(request, 'accounts/role_permission_form.html', {
        'form': form,
        'group': group,
        'page_title': f'Permissions - {group.name}'
    })
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def my_profile(request):
    username = request.user.username
    mobile_number = username.replace('sh_', '')

    shareholder = Shareholder.objects.filter(mobile_number=mobile_number).first()

    if not shareholder:
        return Response({
            "success": False,
            "message": "Shareholder not found",
            "data": None,
            "errors": None
        }, status=404)

    return Response({
        "success": True,
        "message": "Profile fetched successfully",
        "data": {
            "shareholder_name": shareholder.shareholder_name,
            "mobile_number": shareholder.mobile_number,
            "address_line1": shareholder.address_line1 or "",
            "address_line2": shareholder.address_line2 or "",
            "city": shareholder.city or "",
            "state": shareholder.state or "",
            "pincode": shareholder.pincode or "",
        },
        "errors": None
    })
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    serializer = VerifyOtpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    mobile_number = serializer.validated_data['mobile_number']
    otp = serializer.validated_data['otp']

    otp_log = ShareholderOtpLog.objects.filter(
        mobile_number=mobile_number,
        otp_code=otp,
        is_verified=False,
        expires_at__gte=timezone.now()
    ).order_by('-id').first()

    if not otp_log:
        return Response({
            'success': False,
            'message': 'Invalid or expired OTP',
            'data': None,
            'errors': None
        }, status=status.HTTP_400_BAD_REQUEST)

    otp_log.is_verified = True
    otp_log.verified_at = timezone.now()
    otp_log.save()

    username = f"sh_{mobile_number}"

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'first_name': mobile_number,
        }
    )

    token, _ = Token.objects.get_or_create(user=user)

    shareholders = Shareholder.objects.filter(
        mobile_number=mobile_number,
        is_active=True
    )

    shareholder_data = []
    for shareholder in shareholders:
        shareholder_data.append({
            'shareholder_id': shareholder.id,
            'shareholder_code': shareholder.shareholder_code,
            'shareholder_name': shareholder.shareholder_name,
            'mobile_number': shareholder.mobile_number,
        })

    return Response({
        'success': True,
        'message': 'Login successful',
        'data': {
            'access_token': token.key,
            'token_type': 'Token',
            'mobile_number': mobile_number,
            'shareholders': shareholder_data
        },
        'errors': None
    }, status=status.HTTP_200_OK)
    

@login_required
@group_required('ADMIN')
def role_list(request):
    roles = Group.objects.all().order_by('name')
    return render(request, 'accounts/role_list.html', {'roles': roles})


@login_required
@group_required('ADMIN')
def role_create(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Role created successfully.')
            return redirect('role_list')
    else:
        form = RoleForm()

    return render(request, 'accounts/role_form.html', {
        'form': form,
        'page_title': 'Create Role'
    })


@login_required
@group_required('ADMIN')
def user_list(request):
    users = User.objects.exclude(username__startswith='sh_').order_by('username')
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
@group_required('ADMIN')
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()

            full_name = f"{user.first_name} {user.last_name}".strip()

            staff_code = form.cleaned_data.get('staff_code') or f"STF{user.id:03}"
            mobile_number = form.cleaned_data.get('mobile_number', '')
            role_type = form.cleaned_data.get('role_type')
            has_all_branch_access = form.cleaned_data.get('has_all_branch_access', False)
            branches = form.cleaned_data.get('branches')

            staff_user, _ = StaffUser.objects.update_or_create(
                username=user.username,
                defaults={
                    'staff_code': staff_code,
                    'full_name': full_name,
                    'mobile_number': mobile_number,
                    'email': user.email,
                    'password_hash': make_password(form.cleaned_data['password1']),
                    'role_type': role_type,
                    'has_all_branch_access': has_all_branch_access,
                    'is_active': user.is_active,
                }
            )

            StaffBranchAccess.objects.filter(staff_user=staff_user).delete()

            if not has_all_branch_access:
                for branch in branches:
                    StaffBranchAccess.objects.create(
                        staff_user=staff_user,
                        branch=branch
                    )

            messages.success(request, 'User created successfully.')
            return redirect('user_list')
    else:
        form = UserCreateForm()

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'page_title': 'Create User',
        'edit_mode': False
    })
@login_required
@group_required('ADMIN')
def user_edit(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    staff_user_existing = StaffUser.objects.filter(username=user_obj.username).first()

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            user = form.save()

            full_name = f"{user.first_name} {user.last_name}".strip()

            staff_code = form.cleaned_data.get('staff_code') or (
                staff_user_existing.staff_code if staff_user_existing else f"STF{user.id:03}"
            )
            mobile_number = form.cleaned_data.get('mobile_number', '')
            role_type = form.cleaned_data.get('role_type')
            has_all_branch_access = form.cleaned_data.get('has_all_branch_access', False)
            branches = form.cleaned_data.get('branches')

            staff_user, _ = StaffUser.objects.update_or_create(
                username=user.username,
                defaults={
                    'staff_code': staff_code,
                    'full_name': full_name,
                    'mobile_number': mobile_number,
                    'email': user.email,
                    'password_hash': staff_user_existing.password_hash if staff_user_existing else '',
                    'role_type': role_type,
                    'has_all_branch_access': has_all_branch_access,
                    'is_active': user.is_active,
                }
            )

            StaffBranchAccess.objects.filter(staff_user=staff_user).delete()

            if not has_all_branch_access:
                for branch in branches:
                    StaffBranchAccess.objects.create(
                        staff_user=staff_user,
                        branch=branch
                    )

            messages.success(request, 'User updated successfully.')
            return redirect('user_list')
    else:
        form = UserUpdateForm(instance=user_obj)

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'page_title': 'Edit User',
        'edit_mode': True,
        'user_obj': user_obj
    })
    
@login_required
@group_required('ADMIN')
def user_reset_password(request, pk):
    user_obj = get_object_or_404(User, pk=pk)

    if not user_has_role_permission(request.user, 'can_reset_user_password'):
        messages.error(request, 'You do not have permission to reset passwords.')
        return redirect('user_list')

    if user_obj.is_superuser and not request.user.is_superuser:
        messages.error(request, 'You cannot reset superuser password.')
        return redirect('user_list')

    if request.method == 'POST':
        form = AdminResetPasswordForm(request.POST, target_user=user_obj)

        if form.is_valid():
            new_password = form.cleaned_data['new_password']

            user_obj.set_password(new_password)
            user_obj.save(update_fields=['password'])

            staff_user = StaffUser.objects.filter(username=user_obj.username).first()
            if staff_user:
                staff_user.password_hash = make_password(new_password)
                staff_user.save(update_fields=['password_hash'])

            messages.success(request, f'Password reset successfully for {user_obj.username}.')
            return redirect('user_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminResetPasswordForm(target_user=user_obj)

    return render(request, 'accounts/user_reset_password.html', {
        'form': form,
        'user_obj': user_obj,
        'page_title': 'Reset Password'
    })