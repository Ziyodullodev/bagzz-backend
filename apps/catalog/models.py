from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Category(models.Model):
    """A bag type shown under "Shop by categories", e.g. Handle bags or Tote bags."""

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    image = models.ImageField(upload_to="categories/", blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    logo = models.ImageField(upload_to="brands/", blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name


class Shape(models.TextChoices):
    SATCHEL = "satchel", "Satchel"
    TOP_HANDLE = "top_handle", "Top handle"
    TOTE = "tote", "Tote"


def default_look() -> dict:
    return {"shape": Shape.SATCHEL, "body": "#8c3b2e", "trim": "#5e2219", "handle": "#5e2219", "hardware": "#d8c38f"}


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products", null=True, blank=True)
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=160, unique=True)
    subtitle = models.CharField(max_length=160, blank=True, help_text='Short line under the name, e.g. "Wallet with chain".')
    style_code = models.CharField(max_length=40, blank=True, help_text="Shown as Style #…; left empty, the product id is used.")
    color = models.CharField(max_length=40, blank=True)
    description = models.TextField(blank=True)
    material_care = models.TextField(blank=True, help_text='One paragraph, then one care tip per line starting with "- ".')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rating = models.DecimalField(
        max_digits=2, decimal_places=1, default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("5"))],
    )
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True)
    # Colours and silhouette for the SVG placeholder the frontend draws when there is no photo.
    look = models.JSONField(default=default_look, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text='Shown in the "This season\'s latest" carousel.')
    sold_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]

    def __str__(self) -> str:
        return self.name

    @property
    def in_stock(self) -> bool:
        return self.stock > 0

    @property
    def style(self) -> str:
        return self.style_code or f"{self.pk:05d}"
