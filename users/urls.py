from django.urls import path

from .views.auth_views import EmailLoginView, EmailRegisterView, PhoneLoginView

urlpatterns = [
    path('auth/email-login/', EmailLoginView.as_view(), name='email-login'),
    path('auth/email-register/', EmailRegisterView.as_view(), name='email-register'),
    path('auth/phone-login/', PhoneLoginView.as_view(), name='phone-login'),
]