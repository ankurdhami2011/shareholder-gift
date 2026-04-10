from rest_framework import serializers


class StaffLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=128)


class RejectGiftRequestSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField()
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class AcceptGiftRequestSerializer(serializers.Serializer):
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class ShipGiftRequestSerializer(serializers.Serializer):
    courier_name = serializers.CharField(max_length=150)
    tracking_number = serializers.CharField(max_length=150)
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
class DeliverGiftRequestSerializer(serializers.Serializer):
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
