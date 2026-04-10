from django.utils import timezone

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from masters.models import GiftCycle
from shareholders.models import Shareholder
from .models import Share
from .serializers import ShareListSerializer


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def shareholder_share_list(request):
    username = request.user.username

    if not username.startswith('sh_'):
        return Response({
            'success': False,
            'message': 'Invalid shareholder token',
            'data': None,
            'errors': None
        }, status=status.HTTP_401_UNAUTHORIZED)

    mobile_number = username.replace('sh_', '', 1)

    active_cycle = GiftCycle.objects.filter(
        is_active=True,
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    ).first()

    shareholders = Shareholder.objects.filter(
        mobile_number=mobile_number,
        is_active=True
    )

    shares = Share.objects.filter(
        shareholder__in=shareholders,
        is_active=True
    ).select_related('shareholder', 'branch').order_by('id')

    serializer = ShareListSerializer(
        shares,
        many=True,
        context={'active_cycle': active_cycle}
    )

    cycle_data = None
    if active_cycle:
        cycle_data = {
            'gift_cycle_id': active_cycle.id,
            'cycle_code': active_cycle.cycle_code,
            'cycle_name': active_cycle.cycle_name,
            'start_date': active_cycle.start_date,
            'end_date': active_cycle.end_date,
        }

    return Response({
        'success': True,
        'message': 'Shares fetched successfully',
        'data': {
            'gift_cycle': cycle_data,
            'shares': serializer.data
        },
        'errors': None
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def share_delivery_profile(request, share_id):
    username = request.user.username

    if not username.startswith('sh_'):
        return Response({
            'success': False,
            'message': 'Invalid shareholder token',
            'data': None,
            'errors': None
        }, status=status.HTTP_401_UNAUTHORIZED)

    mobile_number = username.replace('sh_', '', 1)

    share = Share.objects.select_related('shareholder').filter(
        id=share_id,
        shareholder__mobile_number=mobile_number,
        shareholder__is_active=True,
        is_active=True
    ).first()

    if not share:
        return Response({
            'success': False,
            'message': 'Share not found',
            'data': None,
            'errors': None
        }, status=status.HTTP_404_NOT_FOUND)

    shareholder = share.shareholder

    return Response({
        'success': True,
        'message': 'Delivery profile fetched successfully',
        'data': {
            'share_id': share.id,
            'share_number': share.share_number,
            'shareholder_name': shareholder.shareholder_name,
            'mobile_number': shareholder.mobile_number,
            'address_line1': shareholder.address_line1 or '',
            'address_line2': shareholder.address_line2 or '',
            'city': shareholder.city or '',
            'state': shareholder.state or '',
            'pincode': shareholder.pincode or '',
        },
        'errors': None
    }, status=status.HTTP_200_OK)