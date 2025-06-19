import uuid
from django.db import models
from django.utils import timezone
from users.models import User, DeviceSession 
from django.utils.translation import gettext_lazy as _


class AuditLog(models.Model):
    id = models.BigAutoField(primary_key=True) # BIGSERIAL in schema
    entity_type = models.CharField(max_length=50, help_text=_('e.g., "User", "Product", "Order"'))
    entity_id = models.UUIDField(blank=True, null=True, help_text=_('UUID of the affected entity'))
    action = models.CharField(max_length=20, choices=[
        ('create', 'Create'), ('update', 'Update'), ('delete', 'Delete'),
        ('view', 'View'), ('login', 'Login'), ('logout', 'Logout'),
        ('refund', 'Refund'), ('ship', 'Ship')
    ])
    old_values = models.JSONField(default=dict, blank=True, null=True, help_text=_('JSON of old field values before update/delete'))
    new_values = models.JSONField(default=dict, blank=True, null=True, help_text=_('JSON of new field values after create/update'))
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='audit_actions',
                              help_text=_('The user who performed the action'))
    ip_address = models.GenericIPAddressField(protocol='both', unpack_ipv4=True, blank=True, null=True)
    device_session = models.ForeignKey(DeviceSession, on_delete=models.SET_NULL, blank=True, null=True, related_name='audit_events')
    timestamp = models.DateTimeField(default=timezone.now)
    api_endpoint = models.CharField(max_length=255, blank=True, null=True, help_text=_('API endpoint accessed'))
    context = models.JSONField(default=dict, blank=True, null=True) # For additional context like request headers, etc.

    class Meta:
        verbose_name = _('audit log')
        verbose_name_plural = _('audit logs')
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['action']),
            models.Index(fields=['actor', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        actor_info = self.actor.email if self.actor else 'System/Anonymous'
        return f"[{self.timestamp}] {actor_info} {self.action} {self.entity_type}:{self.entity_id}"