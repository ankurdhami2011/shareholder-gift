from rest_framework import serializers
from .models import Share


class ShareListSerializer(serializers.ModelSerializer):
    shareholder_id = serializers.IntegerField(source='shareholder.id', read_only=True)
    shareholder_name = serializers.CharField(source='shareholder.shareholder_name', read_only=True)
    branch_id = serializers.IntegerField(source='branch.id', read_only=True)
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True)
    is_selectable = serializers.SerializerMethodField()
    active_request_exists = serializers.SerializerMethodField()

    class Meta:
        model = Share
        fields = [
            'id',
            'shareholder_id',
            'shareholder_name',
            'share_number',
            'certificate_number',
            'branch_id',
            'branch_name',
            'gift_status',
            'stop_reason',
            'is_selectable',
            'active_request_exists',
        ]

    def get_active_request_exists(self, obj):
        active_cycle = self.context.get('active_cycle')
        if not active_cycle:
            return False

        return obj.gift_requests.filter(
            gift_cycle=active_cycle,
            request_status__in=['PENDING', 'ACCEPTED', 'SHIPPED']
        ).exists()

    def get_is_selectable(self, obj):
        active_cycle = self.context.get('active_cycle')
        if obj.gift_status == 'STOPPED':
            return False

        if not active_cycle:
            return False

        active_request_exists = obj.gift_requests.filter(
            gift_cycle=active_cycle,
            request_status__in=['PENDING', 'ACCEPTED', 'SHIPPED']
        ).exists()

        return not active_request_exists