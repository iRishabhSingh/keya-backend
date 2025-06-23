from rest_framework import serializers
from django.utils.translation import gettext as _

class BaseOtpSerializer(serializers.Serializer):
    purpose = serializers.CharField(write_only=True, required=False)
    
    def validate_purpose(self, value):
        """Validate purpose parameter"""
        valid_purposes = ['email-login', 'phone-login', 'email-verify', 'phone-verify']
        if value not in valid_purposes:
            raise serializers.ValidationError(_('Invalid OTP purpose'))
        return value

class OtpRequestSerializer(BaseOtpSerializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    
    def validate(self, attrs):
        email = attrs.get('email')
        phone = attrs.get('phone')
        purpose = attrs.get('purpose', 'login')
        
        if not email and not phone:
            raise serializers.ValidationError(_('Email or phone is required'))
        
        if email and phone:
            raise serializers.ValidationError(_('Provide either email or phone, not both'))
            
        # Set identifier based on input
        attrs['identifier'] = email if email else phone
        return attrs

class OtpVerifySerializer(BaseOtpSerializer):
    otp = serializers.CharField(min_length=6, max_length=6, required=True)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    
    def validate(self, attrs):
        email = attrs.get('email')
        phone = attrs.get('phone')
        purpose = attrs.get('purpose', 'login')
        
        if not email and not phone:
            raise serializers.ValidationError(_('Email or phone is required'))
        
        if email and phone:
            raise serializers.ValidationError(_('Provide either email or phone, not both'))
            
        attrs['identifier'] = email if email else phone
        return attrs