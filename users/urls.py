from django.urls import path

from users.views.otp_views import OtpRequestView, OtpVerifyView

from .views.auth_views import EmailLoginView, EmailRegisterView, PhoneLoginView

urlpatterns = [
    path('auth/email-login/', EmailLoginView.as_view(), name='email-login'),
    path('auth/email-register/', EmailRegisterView.as_view(), name='email-register'),
    path('auth/phone-login/', PhoneLoginView.as_view(), name='phone-login'),
    
    # OTP Endpoints
    path('auth/otp/request/', OtpRequestView.as_view(), name='otp-request'),
    path('auth/otp/verify/', OtpVerifyView.as_view(), name='otp-verify'),
]