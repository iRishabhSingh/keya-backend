import logging
from users.models import User
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.translation import gettext as _
from users.services.otp_service import OTPService
from users.services.email_service import send_otp_email
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers.otp_serializers import OtpRequestSerializer, OtpVerifySerializer

logger = logging.getLogger(__name__)

class OtpRequestView(APIView):
    def post(self, request):
        serializer = OtpRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            purpose = data.get('purpose', 'login')
            identifier = data['identifier']
            
            # Generate and store OTP
            otp = OTPService.store_otp(purpose, identifier)
            
            # Send OTP via appropriate channel
            if '@' in identifier:
                # Email OTP
                success = send_otp_email(identifier, otp, purpose)
                if not success:
                    return Response(
                        {"error": _("Failed to send OTP email")},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                # Phone OTP - log to terminal
                logger.info(f"OTP for {identifier}: {otp}")
                print(f"\n\n--- OTP FOR {identifier} ---")
                print(f"OTP: {otp}")
                print(f"Purpose: {purpose}")
                print(f"Expires in: {settings.OTP_EXPIRY} seconds\n")
                
            return Response({
                "message": _("OTP sent successfully"),
                "expiry": settings.OTP_EXPIRY
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class OtpVerifyView(APIView):
    def post(self, request):
        serializer = OtpVerifySerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            purpose = data.get('purpose', 'login')
            identifier = data['identifier']
            otp = data['otp']
            
            # Verify OTP
            if OTPService.verify_otp(purpose, identifier, otp):
                # Find user by identifier
                if '@' in identifier:
                    user = User.objects.filter(email=identifier).first()
                else:
                    user = User.objects.filter(phone=identifier).first()
                
                if user:
                    # Generate tokens
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "user_id": str(user.id),
                        "identifier": identifier,
                        "is_verified": user.is_verified,
                        "is_active": user.is_active
                    })
                
                # If no user found, still return success but without tokens
                return Response({
                    "message": _("OTP verified successfully"),
                    "user_exists": False
                }, status=status.HTTP_200_OK)
            
            return Response({
                "error": _("Invalid OTP or OTP expired")
            }, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)