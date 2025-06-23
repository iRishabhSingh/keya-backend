import random
from django.conf import settings
from django.core.cache import cache

class OTPService:
    @staticmethod
    def generate_otp(length=6):
        """Generate a random numeric OTP"""
        return ''.join(random.choices('0123456789', k=length))

    @staticmethod
    def create_otp_key(purpose, identifier):
        """Create a Redis key for OTP storage"""
        return f"otp:{purpose}:{identifier}"

    @staticmethod
    def store_otp(purpose, identifier, otp=None):
        """Store OTP in Redis with expiration"""
        if not otp:
            otp = OTPService.generate_otp()
            
        key = OTPService.create_otp_key(purpose, identifier)
        cache.set(key, otp, timeout=settings.OTP_EXPIRY)
        return otp

    @staticmethod
    def verify_otp(purpose, identifier, otp):
        """Verify OTP against stored value"""
        key = OTPService.create_otp_key(purpose, identifier)
        stored_otp = cache.get(key)
        
        if stored_otp and stored_otp == otp:
            cache.delete(key)  # Delete after successful verification
            return True
        return False

    @staticmethod
    def get_otp(purpose, identifier):
        """Retrieve stored OTP without deleting it"""
        key = OTPService.create_otp_key(purpose, identifier)
        return cache.get(key)