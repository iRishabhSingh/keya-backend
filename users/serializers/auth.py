from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext as _
from users.models import Profile, User

class EmailAuthSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,  # Pass as username
                password=password
            )
            
            if not user:
                msg = _('Invalid email or password.')
                raise serializers.ValidationError(msg, code='authorization')
                
            if not user.is_active:
                msg = _('User account is disabled.')
                raise serializers.ValidationError(msg, code='authorization')
                
            # if not user.is_verified:
            #     msg = _('Account not verified. Please check your email.')
            #     raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')
            
        attrs['user'] = user
        return attrs

class PhoneAuthSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')
        
        if phone and password:
            user = authenticate(
                request=self.context.get('request'),
                username=phone,  # Pass phone as username
                password=password
            )
            
            if not user:
                msg = _('Invalid phone number or password.')
                raise serializers.ValidationError(msg, code='authorization')
                
            if not user.is_active:
                msg = _('User account is disabled.')
                raise serializers.ValidationError(msg, code='authorization')
                
            # if not user.is_verified:
            #     msg = _('Account not verified. Please verify your account.')
            #     raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "phone" and "password".')
            raise serializers.ValidationError(msg, code='authorization')
            
        attrs['user'] = user
        return attrs
    
    
class UserRegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    birth_date = serializers.DateField(write_only=True, required=False)
    phone = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'phone', 'marketing_consent',
            'primary_language', 'country', 'user_timezone',
            'first_name', 'last_name', 'birth_date'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'password': {'write_only': True, 'min_length': 8},
        }

    def create(self, validated_data):
        profile_data = {
            'first_name': validated_data.pop('first_name', None),
            'last_name': validated_data.pop('last_name', None),
            'birth_date': validated_data.pop('birth_date', None),
        }
        
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            email=email,
            password=password,
            **validated_data
        )
        
        Profile.objects.create(
            user=user,
            type='personal',
            **{k: v for k, v in profile_data.items() if v is not None}
        )
        
        return user