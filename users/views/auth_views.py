from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.translation import gettext as _
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers.auth import EmailAuthSerializer, PhoneAuthSerializer, UserRegisterSerializer

class EmailLoginView(APIView):
    def post(self, request):
        serializer = EmailAuthSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user_id': str(user.id),
                'email': user.email,
                'is_verified': user.is_verified,
                'is_active': user.is_active
            })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class EmailRegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user_id': str(user.id),
                'email': user.email,
                'phone': user.phone,
                'marketing_consent': user.marketing_consent
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user_id': str(user.id),
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Phone
class PhoneLoginView(APIView):
    def post(self, request):
        serializer = PhoneAuthSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user_id': str(user.id),
                'phone': user.phone,
                'is_verified': user.is_verified,
                'is_active': user.is_active
            })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)