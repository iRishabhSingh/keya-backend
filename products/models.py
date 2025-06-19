import uuid
from django.db import models
from users.models import User
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=[('draft', 'Draft'), ('active', 'Active'), ('archived', 'Archived')], default='draft')
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text=_('Weight in KG'))
    dimensions = models.JSONField(default=dict, blank=True, null=True, help_text=_('e.g., {"length": 10, "width": 5, "height": 2, "unit": "cm"}'))
    available_from = models.DateTimeField(default=timezone.now)
    available_to = models.DateTimeField(blank=True, null=True)
    global_trade_id = models.CharField(max_length=14, blank=True, null=True, unique=True, help_text=_('GTIN/UPC/EAN'))
    harmonized_code = models.CharField(max_length=10, blank=True, null=True, help_text=_('HS code for international trade'))
    carbon_footprint = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text=_('Carbon footprint in kg CO2e'))
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    review_count = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='products_created')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        indexes = [
            models.Index(fields=['status', 'available_from', 'available_to']),
            models.Index(fields=['base_price']),
            models.Index(fields=['global_trade_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        # We need ProductTranslation for the name, but for a quick __str__
        # we can use a placeholder or assume a default translation for the admin.
        # For actual use, you'd fetch the translated name.
        return f"Product {self.id}"


class ProductTranslation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=2, help_text=_('ISO 639-1 language code'))
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    meta_title = models.CharField(max_length=70, blank=True, null=True)
    meta_description = models.CharField(max_length=160, blank=True, null=True)

    class Meta:
        verbose_name = _('product translation')
        verbose_name_plural = _('product translations')
        unique_together = (('product', 'language'),)
        indexes = [
            models.Index(fields=['language', 'name']),
        ]

    def __str__(self):
        return f"{self.product.id} - {self.name} ({self.language})"


class ProductVariant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=50, unique=True)
    attributes = models.JSONField(default=dict, help_text=_('e.g., {"color": "red", "size": "M"}'))
    price_override = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text=_('Overrides product base price if set'))
    inventory_quantity = models.IntegerField(default=0)
    barcode = models.CharField(max_length=20, blank=True, null=True)
    image_url = models.URLField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('product variant')
        verbose_name_plural = _('product variants')
        unique_together = (('product', 'attributes'),) # Ensure unique attribute combinations for a product
        indexes = [
            models.Index(fields=['product', 'sku']),
            models.Index(fields=['inventory_quantity']),
        ]

    def __str__(self):
        return f"{self.product.id} - {self.sku}"


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, editable=False)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    image_url = models.URLField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Collection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, editable=False)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('collection')
        verbose_name_plural = _('collections')
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductCategory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_categories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_products')

    class Meta:
        verbose_name = _('product category')
        verbose_name_plural = _('product categories')
        unique_together = (('product', 'category'),)
        indexes = [
            models.Index(fields=['product', 'category']),
        ]

    def __str__(self):
        return f"{self.product.id} in {self.category.name}"


class ProductTag(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='tag_products')

    class Meta:
        verbose_name = _('product tag')
        verbose_name_plural = _('product tags')
        unique_together = (('product', 'tag'),)
        indexes = [
            models.Index(fields=['product', 'tag']),
        ]

    def __str__(self):
        return f"{self.product.id} tagged with {self.tag.name}"


class ProductCollection(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_collections')
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='collection_products')

    class Meta:
        verbose_name = _('product collection')
        verbose_name_plural = _('product collections')
        unique_together = (('product', 'collection'),)
        indexes = [
            models.Index(fields=['product', 'collection']),
        ]

    def __str__(self):
        return f"{self.product.id} in collection {self.collection.name}"