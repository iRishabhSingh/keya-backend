import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField


class Coupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, help_text=_('Unique coupon code (e.g., SUMMER20)'))
    type = models.CharField(max_length=10, choices=[('flat', 'Flat Amount'), ('percent', 'Percentage')], help_text=_('Type of discount'))
    value = models.DecimalField(max_digits=8, decimal_places=2, help_text=_('Discount value (e.g., 10.00 for $10 or 0.10 for 10%)'))
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    max_usage = models.IntegerField(blank=True, null=True, help_text=_('Maximum number of times this coupon can be used overall'))
    usage_count = models.IntegerField(default=0)
    stackable = models.BooleanField(default=False, help_text=_('Can be combined with other discounts'))
    min_order_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text=_('Minimum order amount for coupon to apply'))
    user_restriction = models.JSONField(default=list, blank=True, null=True, help_text=_('JSON array of user UUIDs or criteria for restriction'))
    country_restriction = ArrayField(models.CharField(max_length=2), blank=True, null=True, help_text=_('List of ISO 3166-1 country codes'))
    category_restriction = ArrayField(models.UUIDField(), blank=True, null=True, help_text=_('List of Category UUIDs'))
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('coupon')
        verbose_name_plural = _('coupons')
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['type']),
        ]

    def __str__(self):
        return self.code


class DiscountRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=[('auto', 'Automatic'), ('code', 'Requires Code')], help_text=_('How the discount is applied'))
    scope = models.CharField(max_length=10, choices=[('product', 'Product'), ('cart', 'Cart'), ('category', 'Category')])
    conditions = models.JSONField(default=dict, help_text=_('JSON defining conditions (e.g., {"min_quantity": 3, "product_ids": []})'))
    effect = models.JSONField(default=dict, help_text=_('JSON defining effect (e.g., {"discount_type": "percent", "value": 15})'))
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('discount rule')
        verbose_name_plural = _('discount rules')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['type', 'scope', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return self.name