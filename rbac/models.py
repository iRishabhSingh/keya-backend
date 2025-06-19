import uuid
from django.db import models
from users.models import User 
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    is_system_role = models.BooleanField(default=False) # e.g., 'Admin', 'Guest'
    scope = models.CharField(max_length=20, choices=[
        ('system', 'System-wide'),
        ('global', 'Global (across tenants)'),
        ('tenant', 'Tenant-specific'),
        ('user', 'User-specific')
    ])
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_system_role']),
        ]

    def __str__(self):
        return self.name


class Permission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100, unique=True, help_text=_('e.g., "order:refund", "product:edit"'))
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, help_text=_('e.g., "product", "order", "user", "marketing"'))
    min_scope = models.CharField(max_length=10, choices=[
        ('system', 'System-wide'),
        ('global', 'Global (across tenants)'),
        ('tenant', 'Tenant-specific'),
        ('user', 'User-specific')
    ], default='global')

    class Meta:
        verbose_name = _('permission')
        verbose_name_plural = _('permissions')
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='permission_roles')
    granted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _('role permission')
        verbose_name_plural = _('role permissions')
        unique_together = (('role', 'permission'),)
        indexes = [
            models.Index(fields=['role', 'permission']),
        ]

    def __str__(self):
        return f"{self.role.name} has {self.permission.code}"


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_users')
    scope_id = models.UUIDField(blank=True, null=True, help_text=_('Optional: ID for tenant, organization, or specific entity for scoped roles'))
    assigned_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _('user role')
        verbose_name_plural = _('user roles')
        unique_together = (('user', 'role', 'scope_id'),) # A user can have a specific role per scope
        indexes = [
            models.Index(fields=['user', 'role']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.user.email} as {self.role.name}"


class UserPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='direct_permissions') # <--- CHANGE THIS RELATED_NAME
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='permission_users')
    grant_type = models.CharField(max_length=1, choices=[('+', 'Grant'), ('-', 'Deny')])
    granted_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _('user permission')
        verbose_name_plural = _('user permissions')
        unique_together = (('user', 'permission'),)
        indexes = [
            models.Index(fields=['user', 'permission']),
            models.Index(fields=['grant_type']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.grant_type} {self.permission.code}"


class SecurityPolicy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    policy_type = models.CharField(max_length=50, choices=[
        ('password', 'Password Policy'),
        ('mfa', 'MFA Policy'),
        ('login_attempt', 'Login Attempt Policy'),
        ('session', 'Session Policy')
    ])
    config = models.JSONField(default=dict, help_text=_('JSON configuration for the policy (e.g., {"min_length": 8, "require_digits": true})'))
    applies_to = models.CharField(max_length=10, choices=[
        ('all', 'All Users'),
        ('roles', 'Specific Roles'),
        ('users', 'Specific Users')
    ])

    class Meta:
        verbose_name = _('security policy')
        verbose_name_plural = _('security policies')
        indexes = [
            models.Index(fields=['policy_type', 'applies_to']),
        ]

    def __str__(self):
        return self.name


class PolicyAssignment(models.Model):
    policy = models.ForeignKey(SecurityPolicy, on_delete=models.CASCADE, related_name='assignments')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, blank=True, null=True, related_name='policy_assignments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='policy_assignments')
    assigned_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _('policy assignment')
        verbose_name_plural = _('policy assignments')
        unique_together = (('policy', 'role'), ('policy', 'user')) # A policy can be assigned to a role OR a user, not both for the same assignment
        indexes = [
            models.Index(fields=['policy', 'role']),
            models.Index(fields=['policy', 'user']),
        ]

    def __str__(self):
        if self.role:
            return f"Policy '{self.policy.name}' assigned to Role '{self.role.name}'"
        elif self.user:
            return f"Policy '{self.policy.name}' assigned to User '{self.user.email}'"
        return f"Policy '{self.policy.name}' assignment"