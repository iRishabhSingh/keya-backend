from twilio.rest import Client
from django.conf import settings
from django.utils.translation import gettext as _

def send_otp_sms(phone, otp, purpose):
    # Customize message based on purpose
    if purpose == 'phone-login':
        message = _("Your login verification code is: {otp}").format(otp=otp)
    elif purpose == 'phone-verify':
        message = _("Your phone verification code is: {otp}").format(otp=otp)
    else:
        message = _("Your verification code is: {otp}").format(otp=otp)
    
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    client.messages.create(
        body=message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone
    )