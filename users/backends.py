from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailPhoneAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        try:
            # Try to find user by email or phone
            user = User.objects.get(Q(email=username) | Q(phone=username))
            
            # Check password and user status
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
            return None
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # Handle case where same value exists in both email and phone fields
            return User.objects.filter(
                Q(email=username) | Q(phone=username)
            ).first()