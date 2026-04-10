import os
import uuid
from audit_logs.utils import create_audit_log

from django.http import HttpResponse
from django.db import transaction
from django.utils import timezone
from notifications.utils import send_request_submitted_sms
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from masters.models import GiftCycle
from shareholders.models import Shareholder
from shares.models import Share

from .models import (
    GiftRequest,
    RequestDeliveryAddress,
    GiftRequestDocument,
    GiftRequestStatusHistory,
)
from .pdf_utils import generate_acknowledgement_pdf
from .serializers import (
    CreateGiftRequestSerializer,
    GiftRequestListSerializer,
    GiftRequestDetailSerializer,
)

from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required


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


def is_staff_user(user):
    return user.groups.filter(name__in=['ADMIN', 'STAFF']).exists()


def is_dispatch_user(user):
    return user.groups.filter(name__in=['ADMIN', 'DISPATCH']).exists()


@login_required
@group_required('ADMIN', 'STAFF', 'DISPATCH')
def staff_request_list(request):
    qs = GiftRequest.objects.select_related(
        'shareholder', 'share', 'branch', 'gift_cycle'
    ).order_by('-id')

    if request.user.groups.filter(name='STAFF').exists():
        qs = qs.filter(request_status='PENDING')
    elif request.user.groups.filter(name='DISPATCH').exists():
        qs = qs.filter(request_status='ACCEPTED')

    return render(request, 'staff/request_list.html', {
        'requests': qs
    })


@login_required
@group_required('ADMIN', 'STAFF')
def accept_request(request, pk):
    obj = GiftRequest.objects.get(pk=pk)

    if obj.request_status != 'PENDING':
        raise PermissionDenied("Invalid status")

    obj.request_status = 'ACCEPTED'
    obj.save(update_fields=['request_status'])

    GiftRequestStatusHistory.objects.create(
        gift_request=obj,
        old_status='PENDING',
        new_status='ACCEPTED',
        changed_by_type='STAFF',
        changed_by_id=request.user.id,
        remarks='Accepted by staff'
    )

    return redirect('staff-web-request-list')


@login_required
@group_required('ADMIN', 'STAFF')
def reject_request(request, pk):
    obj = GiftRequest.objects.get(pk=pk)

    if obj.request_status != 'PENDING':
        raise PermissionDenied("Invalid status")

    reason = request.POST.get('reason', '')

    obj.request_status = 'REJECTED'
    obj.save(update_fields=['request_status'])

    GiftRequestStatusHistory.objects.create(
        gift_request=obj,
        old_status='PENDING',
        new_status='REJECTED',
        changed_by_type='STAFF',
        changed_by_id=request.user.id,
        remarks=reason or 'Rejected by staff'
    )

    return redirect('staff-web-request-list')


@login_required
@group_required('ADMIN', 'DISPATCH')
def create_tracking(request, pk):
    obj = GiftRequest.objects.get(pk=pk)

    if obj.request_status != 'ACCEPTED':
        raise PermissionDenied("Only accepted requests allowed")

    tracking_no = request.POST.get('tracking_number')
    courier = request.POST.get('courier_name')

    obj.request_status = 'SHIPPED'
    obj.tracking_number = tracking_no
    obj.courier_name = courier
    obj.save()

    GiftRequestStatusHistory.objects.create(
        gift_request=obj,
        old_status='ACCEPTED',
        new_status='SHIPPED',
        changed_by_type='STAFF',
        changed_by_id=request.user.id,
        remarks=f"Tracking created: {tracking_no}"
    )

    return redirect('staff-web-request-list')


@login_required
@group_required('ADMIN', 'DISPATCH')
def mark_delivered(request, pk):
    obj = GiftRequest.objects.get(pk=pk)

    if obj.request_status != 'SHIPPED':
        raise PermissionDenied("Only shipped requests allowed")

    obj.request_status = 'DELIVERED'
    obj.save()

    GiftRequestStatusHistory.objects.create(
        gift_request=obj,
        old_status='SHIPPED',
        new_status='DELIVERED',
        changed_by_type='STAFF',
        changed_by_id=request.user.id,
        remarks="Marked delivered"
    )

    return redirect('staff-web-request-list')


def generate_request_no():
    return f"GR-{timezone.now().strftime('%Y%m%d%H%M%S')}"


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_gift_request(request):
    serializer = CreateGiftRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data

    username = request.user.username
    if not username.startswith('sh_'):
        return Response({
            'success': False,
            'message': 'Invalid shareholder token',
            'data': None,
            'errors': None
        }, status=status.HTTP_401_UNAUTHORIZED)

    mobile_number = username.replace('sh_', '', 1)

    login_shareholder = Shareholder.objects.filter(
        mobile_number=mobile_number,
        is_active=True
    ).order_by('id').first()

    if not login_shareholder:
        return Response({
            'success': False,
            'message': 'Invalid user',
            'data': None,
            'errors': None
        }, status=status.HTTP_400_BAD_REQUEST)

    share = Share.objects.select_related('shareholder', 'branch').filter(
        id=data['share_id'],
        shareholder__mobile_number=mobile_number,
        shareholder__is_active=True,
        is_active=True
    ).first()

    if not share:
        return Response({
            'success': False,
            'message': 'Invalid share',
            'data': None,
            'errors': None
        }, status=status.HTTP_400_BAD_REQUEST)

    if share.gift_status == 'STOPPED':
        return Response({
            'success': False,
            'message': 'Gift stopped for this share',
            'data': None,
            'errors': None
        }, status=status.HTTP_400_BAD_REQUEST)

    gift_cycle = GiftCycle.objects.filter(
        id=data['gift_cycle_id'],
        is_active=True
    ).first()

    if not gift_cycle:
        return Response({
            'success': False,
            'message': 'Invalid gift cycle',
            'data': None,
            'errors': None
        }, status=status.HTTP_400_BAD_REQUEST)

    active_exists = GiftRequest.objects.filter(
        share=share,
        gift_cycle=gift_cycle,
        request_status__in=['PENDING', 'ACCEPTED', 'SHIPPED']
    ).exists()

    if active_exists:
        return Response({
            'success': False,
            'message': 'Request already exists for this share in this cycle',
            'data': None,
            'errors': None
        }, status=status.HTTP_400_BAD_REQUEST)

    target_shareholder = share.shareholder

    with transaction.atomic():
        request_no = generate_request_no()

        gift_request = GiftRequest.objects.create(
            request_no=request_no,
            shareholder=target_shareholder,
            share=share,
            gift_cycle=gift_cycle,
            branch=share.branch,
            mobile_number=mobile_number,
            created_by_type='SHAREHOLDER'
        )

        GiftRequestStatusHistory.objects.create(
            gift_request=gift_request,
            old_status=None,
            new_status='PENDING',
            changed_by_type='SHAREHOLDER',
            changed_by_id=login_shareholder.id,
            remarks='Request submitted'
        )

        if data['use_master_address']:
            RequestDeliveryAddress.objects.create(
                gift_request=gift_request,
                recipient_name=target_shareholder.shareholder_name,
                mobile_number=target_shareholder.mobile_number,
                address_line1=target_shareholder.address_line1 or '',
                address_line2=target_shareholder.address_line2 or '',
                city=target_shareholder.city or '',
                state=target_shareholder.state or '',
                pincode=target_shareholder.pincode or '',
                is_from_master_address=True
            )
        else:
            RequestDeliveryAddress.objects.create(
                gift_request=gift_request,
                recipient_name=data['recipient_name'],
                mobile_number=data['mobile_number'],
                address_line1=data['address_line1'],
                address_line2=data.get('address_line2'),
                city=data['city'],
                state=data['state'],
                pincode=data['pincode'],
                is_from_master_address=False
            )

        file = request.FILES['share_certificate']
        file_ext = os.path.splitext(file.name)[1]
        file_name = f"{uuid.uuid4()}{file_ext}"

        folder = os.path.join('media', 'gift_requests', request_no)
        os.makedirs(folder, exist_ok=True)

        file_path = os.path.join(folder, file_name)

        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        GiftRequestDocument.objects.create(
            gift_request=gift_request,
            document_type='SHARE_CERTIFICATE',
            original_file_name=file.name,
            stored_file_name=file_name,
            file_path=file_path,
            mime_type=getattr(file, 'content_type', None),
            file_size=file.size
        )

        create_audit_log(
            module_name='Gift Request',
            table_name='gift_requests_giftrequest',
            record_id=gift_request.id,
            action_type='SUBMIT_REQUEST',
            changed_by_type='SHAREHOLDER',
            changed_by_id=login_shareholder.id,
            branch=gift_request.branch,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            remarks='Gift request submitted by shareholder',
            field_changes=[
                {'column_name': 'request_no', 'old_value': None, 'new_value': gift_request.request_no},
                {'column_name': 'shareholder_id', 'old_value': None, 'new_value': gift_request.shareholder_id},
                {'column_name': 'share_id', 'old_value': None, 'new_value': gift_request.share_id},
                {'column_name': 'gift_cycle_id', 'old_value': None, 'new_value': gift_request.gift_cycle_id},
                {'column_name': 'branch_id', 'old_value': None, 'new_value': gift_request.branch_id},
                {'column_name': 'mobile_number', 'old_value': None, 'new_value': gift_request.mobile_number},
                {'column_name': 'request_status', 'old_value': None, 'new_value': gift_request.request_status},
            ]
        )

        send_request_submitted_sms(gift_request)

    return Response({
        'success': True,
        'message': 'Gift request created successfully',
        'data': {
            'gift_request_id': gift_request.id,
            'request_no': gift_request.request_no,
            'status': gift_request.request_status,
            'acknowledgement_available': True
        },
        'errors': None
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def download_acknowledgement(request, gift_request_id):
    username = request.user.username

    if not username.startswith('sh_'):
        return Response({
            'success': False,
            'message': 'Invalid shareholder token',
            'data': None,
            'errors': None
        }, status=status.HTTP_401_UNAUTHORIZED)

    mobile_number = username.replace('sh_', '', 1)

    obj = GiftRequest.objects.select_related(
        'shareholder',
        'share',
        'branch',
        'gift_cycle',
        'delivery_address'
    ).prefetch_related(
        'status_history'
    ).filter(
        id=gift_request_id,
        mobile_number=mobile_number
    ).first()

    if not obj:
        return Response({
            'success': False,
            'message': 'Gift request not found',
            'data': None,
            'errors': None
        }, status=status.HTTP_404_NOT_FOUND)

    try:
        pdf_bytes = generate_acknowledgement_pdf(obj)
    except Exception as e:
        import traceback
        print("ACK PDF ERROR:", str(e))
        traceback.print_exc()

        return Response({
            'success': False,
            'message': f'Failed to generate acknowledgement: {str(e)}',
            'data': None,
            'errors': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{obj.request_no}.pdf"'
    response['Content-Length'] = len(pdf_bytes)
    return response


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def my_gift_requests(request):
    username = request.user.username

    if not username.startswith('sh_'):
        return Response({
            'success': False,
            'message': 'Invalid shareholder token',
            'data': None,
            'errors': None
        }, status=status.HTTP_401_UNAUTHORIZED)

    mobile_number = username.replace('sh_', '', 1)

    queryset = GiftRequest.objects.select_related(
        'share',
        'branch',
        'shareholder',
        'gift_cycle'
    ).filter(
        mobile_number=mobile_number
    ).order_by('-id')

    request_no = request.GET.get('request_no')
    status_filter = request.GET.get('status')

    if request_no:
        queryset = queryset.filter(request_no__icontains=request_no)

    if status_filter:
        queryset = queryset.filter(request_status=status_filter)

    serializer = GiftRequestListSerializer(queryset, many=True)

    return Response({
        'success': True,
        'message': 'Gift requests fetched successfully',
        'data': {
            'items': serializer.data
        },
        'errors': None
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def my_gift_request_detail(request, gift_request_id):
    username = request.user.username

    if not username.startswith('sh_'):
        return Response({
            'success': False,
            'message': 'Invalid shareholder token',
            'data': None,
            'errors': None
        }, status=status.HTTP_401_UNAUTHORIZED)

    mobile_number = username.replace('sh_', '', 1)

    obj = GiftRequest.objects.select_related(
        'shareholder',
        'share',
        'branch',
        'gift_cycle'
    ).prefetch_related(
        'documents',
        'status_history'
    ).filter(
        id=gift_request_id,
        mobile_number=mobile_number
    ).first()

    if not obj:
        return Response({
            'success': False,
            'message': 'Gift request not found',
            'data': None,
            'errors': None
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = GiftRequestDetailSerializer(obj)

    return Response({
        'success': True,
        'message': 'Gift request details fetched successfully',
        'data': serializer.data,
        'errors': None
    }, status=status.HTTP_200_OK)