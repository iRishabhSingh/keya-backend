from .models import Customer
from users.models import Profile
from rest_framework import serializers

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['type', 'first_name', 'last_name', 'birth_date', 'company', 
                 'tax_id', 'tax_exempt', 'currency', 'communication_prefs', 
                 'saved_payment_methods']

class CustomerSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)
    
    class Meta:
        model = Customer
        fields = '__all__'
        extra_kwargs = {
            'linked_user': {'read_only': True},
            'deleted_at': {'read_only': True},
        }

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        
        # Update linked User if exists
        if instance.linked_user:
            user = instance.linked_user
            if 'email' in validated_data:
                user.email = validated_data['email']
            if 'phone' in validated_data:
                user.phone = validated_data['phone']
            user.save()
        
        # Update Customer
        customer = super().update(instance, validated_data)
        
        # Update Profile
        if profile_data and instance.linked_user:
            profile = instance.linked_user.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
            
        return customer