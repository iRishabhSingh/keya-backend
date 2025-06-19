import uuid
from django.db import models
from users.models import Profile 
from django.utils import timezone
from customers.models import Customer 
from products.models import ProductVariant 
from django.utils.translation import gettext_lazy as _


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True, related_name='carts',
                                help_text=_('Linked to a registered user profile'))
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True, related_name='carts',
                                 help_text=_('Linked to a customer (can be guest or registered)'))
    currency = models.CharField(max_length=3, help_text=_('ISO 4217 currency code'))
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('abandoned', 'Abandoned'), ('converted', 'Converted')], default='active')
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(blank=True, null=True, help_text=_('When the cart session expires'))
    session_data = models.JSONField(default=dict, blank=True, null=True, help_text=_('Ephemeral session data for the cart'))

    class Meta:
        verbose_name = _('cart')
        verbose_name_plural = _('carts')
        indexes = [
            models.Index(fields=['profile', 'status']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Cart {self.id} ({self.status})"


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.IntegerField()
    price_at_addition = models.DecimalField(max_digits=12, decimal_places=2, help_text=_('Price of the variant when added to cart'))
    added_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _('cart item')
        verbose_name_plural = _('cart items')
        unique_together = (('cart', 'product_variant'),) # A cart can have only one entry for a given variant
        indexes = [
            models.Index(fields=['cart', 'product_variant']),
            models.Index(fields=['added_at']),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product_variant.sku} in Cart {self.cart.id}"