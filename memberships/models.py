import uuid
from django.db import models
from users.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class MembershipPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    benefits = models.JSONField(default=list, blank=True, null=True, help_text=_('JSON array of benefits (e.g., ["Free Shipping", "Exclusive Content"])'))
    price = models.DecimalField(max_digits=8, decimal_places=2)
    billing_cycle = models.CharField(max_length=10, choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')], default='monthly')
    trial_days = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('membership plan')
        verbose_name_plural = _('membership plans')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['billing_cycle']),
        ]

    def __str__(self):
        return self.name


class UserMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    membership_plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT, related_name='user_memberships') # PROTECT to avoid deleting plan if users have it
    started_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(blank=True, null=True)
    auto_renew = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('canceled', 'Canceled'), ('expired', 'Expired')], default='active')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('user membership')
        verbose_name_plural = _('user memberships')
        unique_together = (('user', 'membership_plan', 'started_at'),) # A user can have multiple memberships, but starting on different dates for the same plan
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['ends_at']),
        ]

    def __str__(self):
        return f"{self.user.email}'s {self.membership_plan.name} Membership ({self.status})"