import django_filters
from django.db.models import Count, Q
from rest_framework import permissions, viewsets

from .models import Brand, Category, Product
from .serializers import BrandSerializer, CategorySerializer, ProductDetailSerializer, ProductListSerializer


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category__slug")
    brand = django_filters.CharFilter(field_name="brand__slug")
    featured = django_filters.BooleanFilter(field_name="is_featured")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["category", "brand", "featured"]

    def filter_in_stock(self, qs, name, value):
        return qs.filter(stock__gt=0) if value else qs.filter(stock=0)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    lookup_field = "slug"

    def get_queryset(self):
        active = Q(products__is_active=True)
        return Category.objects.filter(is_active=True).annotate(product_count=Count("products", filter=active))


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    lookup_field = "slug"
    queryset = Brand.objects.filter(is_active=True)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:   /api/products/?category=tote-bags&brand=&featured=true&in_stock=true&search=black
            &ordering=price|-price|-rating|-sold_count|-created_at
    detail: /api/products/{slug}/
    """

    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"
    filterset_class = ProductFilter
    search_fields = ["name", "subtitle", "color", "style_code", "brand__name", "category__name"]
    ordering_fields = ["price", "rating", "sold_count", "created_at"]

    def get_queryset(self):
        return (
            Product.objects.filter(is_active=True, category__is_active=True)
            .filter(Q(brand__isnull=True) | Q(brand__is_active=True))
            .select_related("category", "brand")
        )

    def get_serializer_class(self):
        return ProductDetailSerializer if self.action == "retrieve" else ProductListSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        user = self.request.user
        if user.is_authenticated:
            ctx["favorite_ids"] = set(user.favorites.values_list("product_id", flat=True))
        return ctx
