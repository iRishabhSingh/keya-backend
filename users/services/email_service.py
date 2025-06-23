from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from django.template.loader import render_to_string

def send_otp_email(email, otp, purpose):
    # Customize subject based on purpose
    subject_map = {
        'email-login': _("Login Verification Code"),
        'email-verify': _("Email Verification Code"),
        'phone-login': _("Phone Login Verification"),
        'phone-verify': _("Phone Verification Code"),
        'default': _("Your Verification Code"),
    }
    
    subject = subject_map.get(purpose, subject_map['default'])
    
    # Plain text message
    message = _(
        "Your verification code is: {otp}\n\n"
        "This code will expire in {minutes} minutes."
    ).format(otp=otp, minutes=settings.OTP_EXPIRY // 60)
    
    # HTML message
    html_message = render_to_string('emails/otp_email.html', {
        'otp': otp,
        'purpose': purpose,
        'expiry_minutes': settings.OTP_EXPIRY // 60
    })
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        # Log error in production
        print(f"Failed to send email: {str(e)}")
        return False