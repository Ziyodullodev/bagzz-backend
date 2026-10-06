from rest_framework import serializers

from .models import Brand, Category, Product


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "slug", "logo"]


class CategoryRefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)
    cover = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "image", "product_count", "cover"]

    def get_cover(self, obj) -> dict | None:
        """Top product of the category, so the app can draw a tile when the category has no image."""
        p = obj.products.filter(is_active=True).order_by("-is_featured", "-sold_count").first()
        if p is None:
            return None
        image = self.context["request"].build_absolute_uri(p.image.url) if p.image else None
        return {"id": p.id, "name": p.name, "image": image, "look": p.look}


class ProductListSerializer(serializers.ModelSerializer):
    category = CategoryRefSerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    style_code = serializers.CharField(source="style", read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "slug", "name", "subtitle", "style_code", "color", "category", "brand", "price", "old_price",
            "rating", "image", "look", "in_stock", "is_featured", "is_favorite",
        ]

    def get_is_favorite(self, obj) -> bool:
        ids = self.context.get("favorite_ids")
        return obj.id in ids if ids is not None else False


class ProductDetailSerializer(ProductListSerializer):
    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + ["description", "material_care", "stock"]
