from rest_framework import serializers


class SendOtpSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=20)


class VerifyOtpSerializer(serializers.Serializer):
    mobile_number = serializers.CharField(max_length=20)
    otp = serializers.CharField(max_length=20)