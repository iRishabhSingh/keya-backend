import uuid
from django.db import models
from users.models import User 
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), blank=True, null=True, db_index=True, db_collation="und-x-icu")
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_guest = models.BooleanField(default=True)
    linked_user = models.OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='customer_profile',
                                       help_text=_('Link to a registered user if guest converts'))
    first_order_date = models.DateTimeField(blank=True, null=True)
    last_order_date = models.DateTimeField(blank=True, null=True)
    lifetime_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    order_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now) # Add created_at for customer record
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _('customer')
        verbose_name_plural = _('customers')
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['is_guest']),
            models.Index(fields=['linked_user']),
        ]

    def __str__(self):
        return self.email or f"Guest Customer {self.id}"