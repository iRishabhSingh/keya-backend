import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True, db_index=True, blank=True, null=True, db_collation="und-x-icu")
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=20, blank=True, null=True, db_index=True)
    password_hash = models.TextField(blank=True, null=True) # Django handles password hashing, this field is mostly for clarity/compatibility with schema
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    verification_expires = models.DateTimeField(blank=True, null=True)
    mfa_enabled = models.BooleanField(default=False)
    mfa_type = models.CharField(max_length=10, choices=[('sms', 'SMS'), ('totp', 'TOTP'), ('email', 'Email'), ('none', 'None')], default='none')
    mfa_secret = models.TextField(blank=True, null=True) # Should be encrypted at application level if truly sensitive
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    primary_language = models.CharField(max_length=2, default='en', help_text=_('ISO 639-1 language code'))
    country = models.CharField(max_length=2, blank=True, null=True, help_text=_('ISO 3166-1 country code'))
    user_timezone = models.CharField(max_length=50, default='UTC', help_text=_('IANA timezone identifier'))
    profile_image = models.URLField(max_length=255, blank=True, null=True) # Storing CDN URL
    referral_code = models.CharField(max_length=12, unique=True, blank=True, null=True)
    referred_by = models.CharField(max_length=12, blank=True, null=True) # This references another User's referral_code
    marketing_consent = models.BooleanField(default=False)
    consent_updated = models.DateTimeField(blank=True, null=True)
    lifetime_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    loyalty_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    # Required for AbstractBaseUser and PermissionsMixin
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Permissions and Groups
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="users_set", 
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="users_set", 
        related_query_name="user",
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['referral_code']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self._generate_referral_code()
        super().save(*args, **kwargs)

    def _generate_referral_code(self):
        # Simple referral code generation, consider more robust methods
        import random
        import string
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            if not User.objects.filter(referral_code=code).exists():
                return code


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, related_name='profile')
    type = models.CharField(max_length=10, choices=[('personal', 'Personal'), ('business', 'Business')])
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    tax_id = models.CharField(max_length=30, blank=True, null=True)
    tax_exempt = models.BooleanField(default=False)
    currency = models.CharField(max_length=3, default='USD', help_text=_('ISO 4217 currency code'))
    communication_prefs = models.JSONField(default=dict)
    saved_payment_methods = models.JSONField(default=list) # Store non-sensitive tokenized data

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    def __str__(self):
        return f"Profile for {self.user.email}"


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='addresses')
    type = models.CharField(max_length=10, choices=[('shipping', 'Shipping'), ('billing', 'Billing'), ('both', 'Both')])
    label = models.CharField(max_length=50, blank=True, null=True, help_text=_('e.g., Home, Office'))
    line1 = models.CharField(max_length=100)
    line2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=2, help_text=_('ISO 3166-1 country code'))
    is_primary = models.BooleanField(default=False)
    validation_status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('verified', 'Verified'), ('invalid', 'Invalid')], default='pending')
    # geolocation = models.PointField(blank=True, null=True) # Requires PostGIS setup: GEOS, GDAL, libspatialindex

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')
        unique_together = (('profile', 'label'),) # Ensure unique label per profile
        indexes = [
            models.Index(fields=['profile', 'is_primary']),
            models.Index(fields=['country', 'postal_code']),
        ]

    def __str__(self):
        return f"{self.label or self.type} - {self.line1}, {self.city}"


class AuthProvider(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_providers')
    provider = models.CharField(max_length=20, choices=[('google', 'Google'), ('facebook', 'Facebook'), ('apple', 'Apple')])
    provider_uid = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True, null=True, db_index=True, db_collation="und-x-icu")
    refresh_token = models.TextField(blank=True, null=True) # Should be encrypted
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _('auth provider')
        verbose_name_plural = _('auth providers')
        unique_together = (('provider', 'provider_uid'),)
        indexes = [
            models.Index(fields=['user', 'provider']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.provider}"


class DeviceSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_sessions')
    device_hash = models.TextField() # Hashed fingerprint of the device
    ip_address = models.GenericIPAddressField(protocol='both', unpack_ipv4=True) # Stores IPv4 or IPv6
    user_agent = models.TextField()
    country = models.CharField(max_length=2, blank=True, null=True, help_text=_('ISO 3166-1 country code'))
    login_time = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('device session')
        verbose_name_plural = _('device sessions')
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['last_activity']),
        ]

    def __str__(self):
        return f"Session for {self.user.email} on {self.ip_address}"


class AuthHistory(models.Model):
    id = models.BigAutoField(primary_key=True) # BIGSERIAL in schema implies BigAutoField
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_history')
    timestamp = models.DateTimeField(default=timezone.now)
    action = models.CharField(max_length=20, choices=[
        ('login', 'Login'), ('logout', 'Logout'), ('mfa_attempt', 'MFA Attempt'),
        ('password_change', 'Password Change'), ('account_lock', 'Account Lock')
    ])
    method = models.CharField(max_length=20, choices=[('password', 'Password'), ('otp', 'OTP'), ('sso', 'SSO')])
    provider = models.CharField(max_length=20, blank=True, null=True)
    success = models.BooleanField()
    ip_address = models.GenericIPAddressField(protocol='both', unpack_ipv4=True)
    device_id = models.ForeignKey(DeviceSession, on_delete=models.SET_NULL, blank=True, null=True, related_name='auth_events') # Link to DeviceSession
    # api_endpoint removed as it's more for AuditLog, but keep if needed for auth-specific API calls

    class Meta:
        verbose_name = _('auth history')
        verbose_name_plural = _('auth history')
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['success', 'action']),
            models.Index(fields=['ip_address']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.action} ({'Success' if self.success else 'Failure'}) at {self.timestamp}"