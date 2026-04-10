from rest_framework import serializers


class CreateGiftRequestSerializer(serializers.Serializer):
    share_id = serializers.IntegerField()
    gift_cycle_id = serializers.IntegerField()
    use_master_address = serializers.BooleanField()

    recipient_name = serializers.CharField(required=False)
    mobile_number = serializers.CharField(required=False)
    address_line1 = serializers.CharField(required=False)
    address_line2 = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    pincode = serializers.CharField(required=False)

    share_certificate = serializers.FileField()

from rest_framework import serializers
from .models import GiftRequest, RequestDeliveryAddress, GiftRequestDocument, GiftRequestStatusHistory


class GiftRequestListSerializer(serializers.ModelSerializer):
    share_number = serializers.CharField(source='share.share_number', read_only=True)
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True)

    class Meta:
        model = GiftRequest
        fields = [
            'id',
            'request_no',
            'request_status',
            'share_number',
            'branch_name',
            'tracking_number',
            'rejection_reason',
            'submitted_at',
            'accepted_at',
            'rejected_at',
            'shipped_at',
            'delivered_at',
        ]


class RequestDeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestDeliveryAddress
        fields = [
            'recipient_name',
            'mobile_number',
            'address_line1',
            'address_line2',
            'city',
            'state',
            'pincode',
            'is_from_master_address',
        ]


class GiftRequestDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftRequestDocument
        fields = [
            'id',
            'document_type',
            'original_file_name',
            'stored_file_name',
            'file_path',
            'mime_type',
            'file_size',
            'created_at',
        ]


class GiftRequestStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftRequestStatusHistory
        fields = [
            'old_status',
            'new_status',
            'changed_by_type',
            'changed_by_id',
            'remarks',
            'created_at',
        ]


class GiftRequestDetailSerializer(serializers.ModelSerializer):
    shareholder_name = serializers.CharField(source='shareholder.shareholder_name', read_only=True)
    share_number = serializers.CharField(source='share.share_number', read_only=True)
    certificate_number = serializers.CharField(source='share.certificate_number', read_only=True)
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True)
    cycle_code = serializers.CharField(source='gift_cycle.cycle_code', read_only=True)
    cycle_name = serializers.CharField(source='gift_cycle.cycle_name', read_only=True)

    delivery_address = RequestDeliveryAddressSerializer(read_only=True)
    documents = GiftRequestDocumentSerializer(many=True, read_only=True)
    status_history = GiftRequestStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = GiftRequest
        fields = [
            'id',
            'request_no',
            'request_status',
            'shareholder_name',
            'mobile_number',
            'share_number',
            'certificate_number',
            'branch_name',
            'cycle_code',
            'cycle_name',
            'courier_name',
            'tracking_number',
            'rejection_reason',
            'acknowledgement_file_path',
            'submitted_at',
            'accepted_at',
            'rejected_at',
            'shipped_at',
            'delivered_at',
            'delivery_address',
            'documents',
            'status_history',
        ]
        
    def validate(self, data):
        if not data.get('use_master_address'):
            required_fields = [
                'recipient_name',
                'mobile_number',
                'address_line1',
                'city',
                'state',
                'pincode'
            ]
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError(f"{field} is required")

        return data