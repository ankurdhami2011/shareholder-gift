from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from audit_logs.utils import create_audit_log
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from .models import StaffUser
from .serializers import (
    StaffLoginSerializer,
    RejectGiftRequestSerializer,
    AcceptGiftRequestSerializer,
    ShipGiftRequestSerializer,
    DeliverGiftRequestSerializer
)
from notifications.utils import (
    send_request_accepted_sms,
    send_request_rejected_sms,
    send_tracking_created_sms,
    send_request_delivered_sms,
)

from gift_requests.models import GiftRequest, GiftRequestStatusHistory


def get_staff_user_from_token_user(user):
    if not user.username.startswith('staff_'):
        return None
    username = user.username.replace('staff_', '', 1)
    return StaffUser.objects.filter(username=username, is_active=True).first()


def staff_has_branch_access(staff_user, branch_id):
    if not staff_user:
        return False
    if staff_user.has_all_branch_access or staff_user.role_type in ['MASTER_STAFF', 'ADMIN']:
        return True
    return staff_user.branch_accesses.filter(branch_id=branch_id).exists()


@api_view(['POST'])
@permission_classes([AllowAny])
def staff_login(request):
    serializer = StaffLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    staff = StaffUser.objects.filter(username=username, is_active=True).first()

    if not staff or not check_password(password, staff.password_hash):
        return Response({
            'success': False,
            'message': 'Invalid username or password',
            'data': None,
            'errors': None
        }, status=status.HTTP_400_BAD_REQUEST)

    django_username = f"staff_{staff.username}"

    user, created = User.objects.get_or_create(
        username=django_username,
        defaults={'first_name': staff.full_name}
    )

    token, _ = Token.objects.get_or_create(user=user)

    staff.last_login_at = timezone.now()
    staff.save(update_fields=['last_login_at'])

    branches = []
    if staff.has_all_branch_access or staff.role_type in ['MASTER_STAFF', 'ADMIN']:
        branches = list(staff.branch_accesses.select_related('branch').values(
            'branch__id', 'branch__branch_name'
        ))
    else:
        branches = [
            {
                'branch_id': access.branch.id,
                'branch_name': access.branch.branch_name
            }
            for access in staff.branch_accesses.select_related('branch').all()
        ]

    return Response({
        'success': True,
        'message': 'Login successful',
        'data': {
            'access_token': token.key,
            'token_type': 'Token',
            'staff_user': {
                'staff_user_id': staff.id,
                'staff_code': staff.staff_code,
                'full_name': staff.full_name,
                'role_type': staff.role_type,
                'has_all_branch_access': staff.has_all_branch_access,
                'branches': branches
            }
        },
        'errors': None
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def staff_gift_request_list(request):
    staff_user = get_staff_user_from_token_user(request.user)

    if not staff_user:
        return Response({
            'success': False,
            'message': 'Invalid staff token',
            'data': None,
            'errors': None
        }, status=status.HTTP_401_UNAUTHORIZED)

    queryset = GiftRequest.objects.select_related(
        'shareholder', 'share', 'branch', 'gift_cycle'
    ).all().order_by('-id')

    request_no = request.GET.get('request_no')
    status_filter = request.GET.get('status')
    branch_id = request.GET.get('branch_id')

    if request_no:
        queryset = queryset.filter(request_no__icontains=request_no)

    if status_filter:
        queryset = queryset.filter(request_status=status_filter)

    if branch_id:
        queryset = queryset.filter(branch_id=branch_id)

    if not (staff_user.has_all_branch_access or staff_user.role_type in ['MASTER_STAFF', 'ADMIN']):
        allowed_branch_ids = list(staff_user.branch_accesses.values_list('branch_id', flat=True))
        queryset = queryset.filter(branch_id__in=allowed_branch_ids)

    items = []
    for obj in queryset:
        items.append({
            'gift_request_id': obj.id,
            'request_no': obj.request_no,
            'shareholder_name': obj.shareholder.shareholder_name,
            'mobile_number': obj.mobile_number,
            'share_number': obj.share.share_number,
            'branch_id': obj.branch.id,
            'branch_name': obj.branch.branch_name,
            'request_status': obj.request_status,
            'tracking_number': obj.tracking_number,
            'rejection_reason': obj.rejection_reason,
            'submitted_at': obj.submitted_at,
        })

    return Response({
        'success': True,
        'message': 'Gift requests fetched successfully',
        'data': {
            'items': items
        },
        'errors': None
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def accept_gift_request(request, gift_request_id):
    staff_user = get_staff_user_from_token_user(request.user)

    if not staff_user:
        return Response({'success': False, 'message': 'Invalid staff token'}, status=401)

    serializer = AcceptGiftRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    obj = GiftRequest.objects.select_related('branch').filter(id=gift_request_id).first()

    if not obj:
        return Response({'success': False, 'message': 'Gift request not found'}, status=404)

    if not staff_has_branch_access(staff_user, obj.branch_id):
        return Response({'success': False, 'message': 'No branch access'}, status=403)

    if obj.request_status != 'PENDING':
        return Response({'success': False, 'message': 'Only pending requests can be accepted'}, status=400)

    with transaction.atomic():
        old_status = obj.request_status
        old_accepted_at = obj.accepted_at
        old_updated_by_type = obj.updated_by_type
        old_updated_by_id = obj.updated_by_id

        obj.request_status = 'ACCEPTED'
        obj.accepted_at = timezone.now()
        obj.updated_by_type = 'STAFF'
        obj.updated_by_id = staff_user.id
        obj.save()

        GiftRequestStatusHistory.objects.create(
            gift_request=obj,
            old_status=old_status,
            new_status='ACCEPTED',
            changed_by_type='STAFF',
            changed_by_id=staff_user.id,
            remarks=serializer.validated_data.get('remarks')
        )

        create_audit_log(
            module_name='Gift Request',
            table_name='gift_requests_giftrequest',
            record_id=obj.id,
            action_type='ACCEPT_REQUEST',
            changed_by_type='STAFF',
            changed_by_id=staff_user.id,
            branch=obj.branch,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            remarks=serializer.validated_data.get('remarks') or 'Request accepted by staff',
            field_changes=[
                {'column_name': 'request_status', 'old_value': old_status, 'new_value': obj.request_status},
                {'column_name': 'accepted_at', 'old_value': old_accepted_at, 'new_value': obj.accepted_at},
                {'column_name': 'updated_by_type', 'old_value': old_updated_by_type, 'new_value': obj.updated_by_type},
                {'column_name': 'updated_by_id', 'old_value': old_updated_by_id, 'new_value': obj.updated_by_id},
            ]
        )
        send_request_accepted_sms(obj)
    return Response({
        'success': True,
        'message': 'Request accepted successfully',
        'data': {
            'gift_request_id': obj.id,
            'request_no': obj.request_no,
            'request_status': obj.request_status,
            'accepted_at': obj.accepted_at
        },
        'errors': None
    }, status=200)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def reject_gift_request(request, gift_request_id):
    staff_user = get_staff_user_from_token_user(request.user)

    if not staff_user:
        return Response({'success': False, 'message': 'Invalid staff token'}, status=401)

    serializer = RejectGiftRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    obj = GiftRequest.objects.select_related('branch').filter(id=gift_request_id).first()

    if not obj:
        return Response({'success': False, 'message': 'Gift request not found'}, status=404)

    if not staff_has_branch_access(staff_user, obj.branch_id):
        return Response({'success': False, 'message': 'No branch access'}, status=403)

    if obj.request_status != 'PENDING':
        return Response({'success': False, 'message': 'Only pending requests can be rejected'}, status=400)

    with transaction.atomic():
        old_status = obj.request_status
        old_rejection_reason = obj.rejection_reason
        old_rejected_at = obj.rejected_at
        old_updated_by_type = obj.updated_by_type
        old_updated_by_id = obj.updated_by_id

        obj.request_status = 'REJECTED'
        obj.rejection_reason = serializer.validated_data['rejection_reason']
        obj.rejected_at = timezone.now()
        obj.updated_by_type = 'STAFF'
        obj.updated_by_id = staff_user.id
        obj.save()

        GiftRequestStatusHistory.objects.create(
            gift_request=obj,
            old_status=old_status,
            new_status='REJECTED',
            changed_by_type='STAFF',
            changed_by_id=staff_user.id,
            remarks=serializer.validated_data.get('remarks')
        )

        create_audit_log(
            module_name='Gift Request',
            table_name='gift_requests_giftrequest',
            record_id=obj.id,
            action_type='REJECT_REQUEST',
            changed_by_type='STAFF',
            changed_by_id=staff_user.id,
            branch=obj.branch,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            remarks=serializer.validated_data.get('remarks') or 'Request rejected by staff',
            field_changes=[
                {'column_name': 'request_status', 'old_value': old_status, 'new_value': obj.request_status},
                {'column_name': 'rejection_reason', 'old_value': old_rejection_reason, 'new_value': obj.rejection_reason},
                {'column_name': 'rejected_at', 'old_value': old_rejected_at, 'new_value': obj.rejected_at},
                {'column_name': 'updated_by_type', 'old_value': old_updated_by_type, 'new_value': obj.updated_by_type},
                {'column_name': 'updated_by_id', 'old_value': old_updated_by_id, 'new_value': obj.updated_by_id},
            ]
        )
        send_request_rejected_sms(obj)
    return Response({
        'success': True,
        'message': 'Request rejected successfully',
        'data': {
            'gift_request_id': obj.id,
            'request_no': obj.request_no,
            'request_status': obj.request_status,
            'rejection_reason': obj.rejection_reason,
            'rejected_at': obj.rejected_at
        },
        'errors': None
    }, status=200)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def ship_gift_request(request, gift_request_id):
    staff_user = get_staff_user_from_token_user(request.user)

    if not staff_user:
        return Response({'success': False, 'message': 'Invalid staff token'}, status=401)

    serializer = ShipGiftRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    obj = GiftRequest.objects.select_related('branch').filter(id=gift_request_id).first()

    if not obj:
        return Response({'success': False, 'message': 'Gift request not found'}, status=404)

    if not staff_has_branch_access(staff_user, obj.branch_id):
        return Response({'success': False, 'message': 'No branch access'}, status=403)

    if obj.request_status != 'ACCEPTED':
        return Response({'success': False, 'message': 'Only accepted requests can be shipped'}, status=400)

    with transaction.atomic():
        old_status = obj.request_status
        old_courier_name = obj.courier_name
        old_tracking_number = obj.tracking_number
        old_shipped_at = obj.shipped_at
        old_updated_by_type = obj.updated_by_type
        old_updated_by_id = obj.updated_by_id

        obj.request_status = 'SHIPPED'
        obj.courier_name = serializer.validated_data['courier_name']
        obj.tracking_number = serializer.validated_data['tracking_number']
        obj.shipped_at = timezone.now()
        obj.updated_by_type = 'STAFF'
        obj.updated_by_id = staff_user.id
        obj.save()

        GiftRequestStatusHistory.objects.create(
            gift_request=obj,
            old_status=old_status,
            new_status='SHIPPED',
            changed_by_type='STAFF',
            changed_by_id=staff_user.id,
            remarks=serializer.validated_data.get('remarks')
        )

        create_audit_log(
            module_name='Gift Request',
            table_name='gift_requests_giftrequest',
            record_id=obj.id,
            action_type='SHIP_REQUEST',
            changed_by_type='STAFF',
            changed_by_id=staff_user.id,
            branch=obj.branch,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            remarks=serializer.validated_data.get('remarks') or 'Request shipped by staff',
            field_changes=[
                {'column_name': 'request_status', 'old_value': old_status, 'new_value': obj.request_status},
                {'column_name': 'courier_name', 'old_value': old_courier_name, 'new_value': obj.courier_name},
                {'column_name': 'tracking_number', 'old_value': old_tracking_number, 'new_value': obj.tracking_number},
                {'column_name': 'shipped_at', 'old_value': old_shipped_at, 'new_value': obj.shipped_at},
                {'column_name': 'updated_by_type', 'old_value': old_updated_by_type, 'new_value': obj.updated_by_type},
                {'column_name': 'updated_by_id', 'old_value': old_updated_by_id, 'new_value': obj.updated_by_id},
            ]
        )
        send_tracking_created_sms(obj)
    return Response({
        'success': True,
        'message': 'Tracking details updated successfully',
        'data': {
            'gift_request_id': obj.id,
            'request_no': obj.request_no,
            'request_status': obj.request_status,
            'courier_name': obj.courier_name,
            'tracking_number': obj.tracking_number,
            'shipped_at': obj.shipped_at
        },
        'errors': None
    }, status=200)
    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deliver_gift_request(request, gift_request_id):
    staff_user = get_staff_user_from_token_user(request.user)

    if not staff_user:
        return Response({
            'success': False,
            'message': 'Invalid staff token',
            'data': None,
            'errors': None
        }, status=401)

    serializer = DeliverGiftRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    obj = GiftRequest.objects.select_related('branch').filter(id=gift_request_id).first()

    if not obj:
        return Response({
            'success': False,
            'message': 'Gift request not found',
            'data': None,
            'errors': None
        }, status=404)

    if not staff_has_branch_access(staff_user, obj.branch_id):
        return Response({
            'success': False,
            'message': 'No branch access',
            'data': None,
            'errors': None
        }, status=403)

    if obj.request_status != 'SHIPPED':
        return Response({
            'success': False,
            'message': 'Only shipped requests can be marked as delivered',
            'data': None,
            'errors': None
        }, status=400)

    with transaction.atomic():
        old_status = obj.request_status
        old_delivered_at = obj.delivered_at
        old_updated_by_type = obj.updated_by_type
        old_updated_by_id = obj.updated_by_id

        obj.request_status = 'DELIVERED'
        obj.delivered_at = timezone.now()
        obj.updated_by_type = 'STAFF'
        obj.updated_by_id = staff_user.id
        obj.save()

        GiftRequestStatusHistory.objects.create(
            gift_request=obj,
            old_status=old_status,
            new_status='DELIVERED',
            changed_by_type='STAFF',
            changed_by_id=staff_user.id,
            remarks=serializer.validated_data.get('remarks')
        )

        create_audit_log(
            module_name='Gift Request',
            table_name='gift_requests_giftrequest',
            record_id=obj.id,
            action_type='DELIVER_REQUEST',
            changed_by_type='STAFF',
            changed_by_id=staff_user.id,
            branch=obj.branch,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            remarks=serializer.validated_data.get('remarks') or 'Request marked delivered by staff',
            field_changes=[
                {'column_name': 'request_status', 'old_value': old_status, 'new_value': obj.request_status},
                {'column_name': 'delivered_at', 'old_value': old_delivered_at, 'new_value': obj.delivered_at},
                {'column_name': 'updated_by_type', 'old_value': old_updated_by_type, 'new_value': obj.updated_by_type},
                {'column_name': 'updated_by_id', 'old_value': old_updated_by_id, 'new_value': obj.updated_by_id},
            ]
        )
        send_request_delivered_sms(obj)
    return Response({
        'success': True,
        'message': 'Request marked as delivered successfully',
        'data': {
            'gift_request_id': obj.id,
            'request_no': obj.request_no,
            'request_status': obj.request_status,
            'delivered_at': obj.delivered_at
        },
        'errors': None
    }, status=200)