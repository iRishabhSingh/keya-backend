import uuid
from django.db import models
from django.utils import timezone
from customers.models import Customer 
from users.models import Profile, Address
from products.models import ProductVariant
from django.utils.translation import gettext_lazy as _


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True, related_name='orders',
                                help_text=_('Link to the user profile if applicable'))
    currency = models.CharField(max_length=3, help_text=_('ISO 4217 currency code'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed'),
        ('refunded', 'Refunded'), ('partially_refunded', 'Partially Refunded')
    ], default='pending')
    shipping_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'), ('processing', 'Processing'), ('shipped', 'Shipped'),
        ('delivered', 'Delivered'), ('returned', 'Returned'), ('canceled', 'Canceled')
    ], default='pending')
    billing_address = models.ForeignKey(Address, on_delete=models.SET_NULL, blank=True, null=True, related_name='billed_orders')
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, blank=True, null=True, related_name='shipped_orders')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    acquisition_channel = models.CharField(max_length=20, blank=True, null=True, help_text=_('e.g., "organic", "paid_search", "referral"'))
    fraud_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    carbon_offset = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text=_('Amount of carbon offset purchased with the order'))
    lifetime_value_segment = models.CharField(max_length=10, blank=True, null=True,
                                              help_text=_('e.g., "high_value", "medium", "low" (for analytics)'))

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        indexes = [
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['shipping_status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Order {self.id} for {self.customer.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name='order_items') # PROTECT to prevent deleting variant if in an order
    quantity = models.IntegerField()
    price_at_purchase = models.DecimalField(max_digits=12, decimal_places=2, help_text=_('Price of the variant at the time of purchase'))
    discount_applied = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')
        unique_together = (('order', 'product_variant'),) # An order can have only one entry for a given variant
        indexes = [
            models.Index(fields=['order', 'product_variant']),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product_variant.sku} in Order {self.order.id}"