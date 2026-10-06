from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalog.models import Brand, Category, Product

CARE = (
    "Every bag is made from carefully selected materials. Handle it with care for a longer life.\n"
    "- Keep away from direct sunlight, heat and rain. If it gets wet, dry it right away with a soft cloth.\n"
    "- Store it in the dust bag it came in.\n"
    "- Clean with a soft, dry cloth."
)

CATEGORIES = ["Handle bags", "Crossbody bags", "Shoulder bags", "Tote bags"]
BRANDS = ["Maison Lune", "Atelier Noir", "Verda"]

# slug, name, subtitle, category, brand, style, colour, price, old price, stock, featured, look, description
PRODUCTS = [
    ("artsy", "Artsy", "Wallet with chain", "Handle bags", "Maison Lune", "36252 0YK0G 1000", "Burgundy",
     "564", None, 12, True, {"shape": "satchel", "body": "#8c3b2e", "trim": "#6d2a20", "handle": "#5e2219", "hardware": "#d8c38f"},
     "A rounded doctor bag in smooth calf leather with a ring charm on the side. "
     "The top zip opens wide, and the inside has a zipped pocket and two slip pockets."),
    ("berkely", "Berkely", "Top handle bag", "Handle bags", "Atelier Noir", "36252 0YK0G 2040", "Pewter",
     "649", "720", 8, True, {"shape": "top_handle", "body": "#8f8a80", "trim": "#c9c2b4", "handle": "#3b3833", "hardware": "#d9d4c7"},
     "A structured top handle bag with a metallic finish and a contrast front flap. "
     "Carry it by hand or clip on the detachable strap."),
    ("capucinus", "Capucinus", "Wallet with chain", "Shoulder bags", "Atelier Noir", "36252 0YK0G 3100", "Black",
     "1290", None, 5, True, {"shape": "top_handle", "body": "#1d1d1d", "trim": "#333333", "handle": "#111111", "hardware": "#c0c0c0"},
     "Grained black leather with a fold-over flap and a detachable chain strap. "
     "Fits a phone, cardholder and keys."),
    ("monogram", "Monogram", "Foldable tote", "Tote bags", "Verda", "9242 0YK0G 211", "Khaki",
     "1638", None, 20, False, {"shape": "tote", "body": "#6f7a5c", "trim": "#8a5a3c", "handle": "#8a5a3c", "hardware": "#d8c38f"},
     "A light nylon tote with leather handles that folds flat into its own flap. "
     "Roomy enough for a laptop and a change of clothes."),
    ("sling-black", "Artsy Sling", "Black sling bag", "Crossbody bags", "Maison Lune", "36252 0YK0G 4410", "Black",
     "420", None, 15, False, {"shape": "top_handle", "body": "#262626", "trim": "#3a3a3a", "handle": "#1a1a1a", "hardware": "#d8c38f"},
     "A compact crossbody with an adjustable strap and a magnetic flap. Small outside, surprisingly roomy inside."),
    ("berkely-sling", "Berkely Sling", "Crossbody in suede", "Crossbody bags", "Atelier Noir", "36252 0YK0G 4520", "Tan",
     "385", "450", 9, False, {"shape": "satchel", "body": "#b07a4a", "trim": "#8d5e35", "handle": "#6b4426", "hardware": "#e0cfa0"},
     "Soft suede with a curved top zip and a wide woven strap for all-day wear."),
    ("riviera", "Riviera", "Sling bag, blue", "Crossbody bags", "Verda", "9242 0YK0G 515", "Navy",
     "310", None, 0, False, {"shape": "top_handle", "body": "#22355e", "trim": "#2f4677", "handle": "#18264a", "hardware": "#cfd6e4"},
     "A navy sling in coated canvas with a front zip pocket. Water resistant."),
    ("marlowe", "Marlowe", "Shoulder bag", "Shoulder bags", "Maison Lune", "36252 0YK0G 5160", "Cream",
     "890", None, 6, True, {"shape": "satchel", "body": "#e8dcc5", "trim": "#cdbb98", "handle": "#9b7b4f", "hardware": "#c9a74f"},
     "Pebbled cream leather with a slim shoulder strap and a gold-tone clasp."),
    ("harbor", "Harbor", "Everyday tote", "Tote bags", "Verda", "9242 0YK0G 620", "Sand",
     "275", None, 25, False, {"shape": "tote", "body": "#cdb592", "trim": "#7d5a3a", "handle": "#7d5a3a", "hardware": "#e6d9b8"},
     "A heavy cotton canvas tote with leather trims and an inner zip pocket."),
    ("noor", "Noor", "Mini handle bag", "Handle bags", "Atelier Noir", "36252 0YK0G 7010", "Olive",
     "540", None, 7, False, {"shape": "top_handle", "body": "#5b6447", "trim": "#46503a", "handle": "#2f3527", "hardware": "#d8c38f"},
     "A small structured handle bag with a removable strap and a turn-lock closure."),
]


class Command(BaseCommand):
    help = "Create demo categories, brands and bags matching the Figma design. Safe to run again."

    def add_arguments(self, parser):
        parser.add_argument("--if-empty", action="store_true", help="Do nothing when products already exist (for deploy scripts).")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["if_empty"] and Product.objects.exists():
            self.stdout.write("Catalogue already has products, skipping.")
            return
        cats = {}
        for i, name in enumerate(CATEGORIES):
            slug = name.lower().replace(" ", "-")
            cats[name], _ = Category.objects.update_or_create(slug=slug, defaults={"name": name, "sort_order": i})
        brands = {}
        for i, name in enumerate(BRANDS):
            slug = name.lower().replace(" ", "-")
            brands[name], _ = Brand.objects.update_or_create(slug=slug, defaults={"name": name, "sort_order": i})

        for order, (slug, name, subtitle, cat, brand, style, color, price, old, stock, featured, look, desc) in enumerate(PRODUCTS):
            product, created = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name, "subtitle": subtitle, "category": cats[cat], "brand": brands[brand],
                    "style_code": style, "color": color, "price": Decimal(price),
                    "old_price": Decimal(old) if old else None, "is_featured": featured, "look": look,
                    "description": desc, "material_care": CARE, "rating": Decimal("4.5"),
                    "sold_count": 100 - order * 7,
                },
            )
            # Keep stock that staff changed in the admin; set it only for new products.
            if created:
                product.stock = stock
                product.save(update_fields=["stock"])

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(CATEGORIES)} categories, {len(BRANDS)} brands and {len(PRODUCTS)} products."
        ))
