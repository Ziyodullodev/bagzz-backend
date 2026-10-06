from django.contrib import admin
from django.utils.html import format_html

from .models import Brand, Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "sort_order", "is_active"]
    list_editable = ["sort_order", "is_active"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["thumb", "name", "category", "brand", "price", "stock", "sold_count", "is_featured", "is_active"]
    list_display_links = ["thumb", "name"]
    list_editable = ["price", "stock", "is_featured", "is_active"]
    list_filter = ["category", "brand", "is_featured", "is_active"]
    search_fields = ["name", "slug", "subtitle", "style_code", "brand__name"]
    prepopulated_fields = {"slug": ("name",)}
    list_select_related = ["category", "brand"]
    fieldsets = [
        (None, {"fields": ["name", "slug", "subtitle", "category", "brand", "style_code", "color"]}),
        ("Price and stock", {"fields": ["price", "old_price", "stock", "rating"]}),
        ("Content", {"fields": ["description", "material_care", "image", "look"]}),
        ("Visibility", {"fields": ["is_active", "is_featured", "sold_count"]}),
    ]

    @admin.display(description="")
    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px" />', obj.image.url)
        return format_html('<span style="display:inline-block;width:40px;height:24px;background:{}"></span>', obj.look.get("body", "#ccc"))
