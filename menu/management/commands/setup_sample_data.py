"""
Django management command to populate the database with sample data.
Safely adds data only if it doesn't exist.
"""

from decimal import Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from menu.models import Dish, Menu

User = get_user_model()


class Command(BaseCommand):
    """Command to populate the database with sample data."""

    help = "Populates the database with sample users, menus, and dishes (safely)."

    def handle(self, *args: Any, **options: Any) -> None:
        """Handle the command execution."""
        self.stdout.write("Checking and populating sample data...")

        with transaction.atomic():
            # --- USERS ---
            admin_email = "admin@example.com"
            if not User.objects.filter(email=admin_email).exists():
                User.objects.create_superuser(email=admin_email, password="password123", name="Super Admin")
                self.stdout.write(self.style.SUCCESS(f"Created admin: {admin_email}"))
            else:
                self.stdout.write(f"Admin {admin_email} already exists.")

            user_email = "user@example.com"
            if not User.objects.filter(email=user_email).exists():
                User.objects.create_user(email=user_email, password="password123", name="Regular Joe")
                self.stdout.write(self.style.SUCCESS(f"Created user: {user_email}"))
            else:
                self.stdout.write(f"User {user_email} already exists.")

            # --- MENUS AND DISHES ---

            # 1. Breakfast
            breakfast_menu, created = Menu.objects.get_or_create(
                name="Breakfast Specials",
                defaults={"description": "Start your day with energy!"},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created menu: {breakfast_menu.name}"))

            self._create_dish_if_missing(
                menu=breakfast_menu,
                name="Classic Pancakes",
                description="Fluffy pancakes with maple syrup.",
                price=Decimal("15.99"),
                prep_time=15,
                is_vegetarian=True,
            )
            self._create_dish_if_missing(
                menu=breakfast_menu,
                name="Full English Breakfast",
                description="Eggs, bacon, sausages, beans, and toast.",
                price=Decimal("25.50"),
                prep_time=20,
                is_vegetarian=False,
            )
            self._create_dish_if_missing(
                menu=breakfast_menu,
                name="Avocado Toast",
                description="Sourdough bread with smashed avocado and chili flakes.",
                price=Decimal("12.50"),
                prep_time=10,
                is_vegetarian=True,
            )

            # 2. Italian
            italian_menu, created = Menu.objects.get_or_create(
                name="Italian Dinner",
                defaults={"description": "Authentic taste of Italy."},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created menu: {italian_menu.name}"))

            self._create_dish_if_missing(
                menu=italian_menu,
                name="Spaghetti Carbonara",
                description="Pasta with guanciale, egg, and pecorino romano.",
                price=Decimal("32.00"),
                prep_time=25,
                is_vegetarian=False,
            )
            self._create_dish_if_missing(
                menu=italian_menu,
                name="Margherita Pizza",
                description="Tomato sauce, mozzarella di bufala, basil.",
                price=Decimal("28.00"),
                prep_time=20,
                is_vegetarian=True,
            )
            self._create_dish_if_missing(
                menu=italian_menu,
                name="Tiramisu",
                description="Classic coffee-flavoured Italian dessert.",
                price=Decimal("18.00"),
                prep_time=10,
                is_vegetarian=True,
            )
            self._create_dish_if_missing(
                menu=italian_menu,
                name="Lasagna Bolognese",
                description="Layers of pasta, meat sauce, and bechamel.",
                price=Decimal("30.00"),
                prep_time=45,
                is_vegetarian=False,
            )

            # 3. Lunch Deals
            lunch_menu, created = Menu.objects.get_or_create(
                name="Lunch Deals",
                defaults={"description": "Quick and tasty meals for your break."},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created menu: {lunch_menu.name}"))

            self._create_dish_if_missing(
                menu=lunch_menu,
                name="Cheeseburger",
                description="Beef patty, cheddar, lettuce, tomato, fries.",
                price=Decimal("12.50"),
                prep_time=15,
                is_vegetarian=False,
            )
            self._create_dish_if_missing(
                menu=lunch_menu,
                name="Caesar Salad",
                description="Romaine lettuce, croutons, parmesan, caesar dressing.",
                price=Decimal("10.00"),
                prep_time=10,
                is_vegetarian=False,
            )
            self._create_dish_if_missing(
                menu=lunch_menu,
                name="Club Sandwich",
                description="Chicken, bacon, lettuce, tomato, mayo.",
                price=Decimal("11.50"),
                prep_time=12,
                is_vegetarian=False,
            )

            # 4. Vegan Corner
            vegan_menu, created = Menu.objects.get_or_create(
                name="Vegan Corner",
                defaults={"description": "100% plant-based deliciousness."},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created menu: {vegan_menu.name}"))

            self._create_dish_if_missing(
                menu=vegan_menu,
                name="Buddha Bowl",
                description="Quinoa, avocado, chickpeas, sweet potato, tahini.",
                price=Decimal("14.00"),
                prep_time=15,
                is_vegetarian=True,
            )
            self._create_dish_if_missing(
                menu=vegan_menu,
                name="Lentil Curry",
                description="Red lentils, coconut milk, spinach, basmati rice.",
                price=Decimal("13.50"),
                prep_time=20,
                is_vegetarian=True,
            )

            # 5. Desserts
            dessert_menu, created = Menu.objects.get_or_create(
                name="Dessert Heaven",
                defaults={"description": "Sweet treats to finish your meal."},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created menu: {dessert_menu.name}"))

            self._create_dish_if_missing(
                menu=dessert_menu,
                name="New York Cheesecake",
                description="Creamy cheesecake with berry compote.",
                price=Decimal("8.50"),
                prep_time=5,
                is_vegetarian=True,
            )
            self._create_dish_if_missing(
                menu=dessert_menu,
                name="Chocolate Brownie",
                description="Warm brownie with vanilla ice cream.",
                price=Decimal("7.50"),
                prep_time=10,
                is_vegetarian=True,
            )

            # 6. Drinks (Empty)
            drinks_menu, created = Menu.objects.get_or_create(
                name="Seasonal Drinks",
                defaults={"description": "Refreshing beverages (Currently empty)."},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created menu: {drinks_menu.name}"))

        self.stdout.write(self.style.SUCCESS("Sample data check/population finished!"))

    def _create_dish_if_missing(self, menu, name, **kwargs):
        """Helper to create a dish only if it doesn't exist."""
        _, created = Dish.objects.get_or_create(menu=menu, name=name, defaults=kwargs)
        if created:
            self.stdout.write(self.style.SUCCESS(f"  + Added dish: {name}"))
