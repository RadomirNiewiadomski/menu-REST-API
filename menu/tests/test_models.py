"""
Tests for the menu app models.
"""

from decimal import Decimal

import pytest

from menu import models


@pytest.mark.django_db
def test_create_menu_successful():
    """Test creating a menu successfully."""
    name = "Lunch Menu"
    description = "Our daily lunch specials."

    menu = models.Menu.objects.create(
        name=name,
        description=description,
    )

    assert menu.name == name
    assert menu.description == description
    assert str(menu) == name
    assert menu.created_at is not None
    assert menu.updated_at is not None


@pytest.mark.django_db
def test_create_dish_successful():
    """Test creating a dish successfully."""
    menu = models.Menu.objects.create(name="Dinner", description="Delicious dinner")
    dish = models.Dish.objects.create(
        menu=menu,
        name="Spaghetti Carbonara",
        description="Classic Italian pasta with eggs, cheese, and bacon.",
        price=Decimal("45.50"),
        prep_time=20,
        is_vegetarian=False,
    )

    assert dish.name == "Spaghetti Carbonara"
    assert dish.price == Decimal("45.50")
    assert dish.menu == menu
    assert dish.is_vegetarian is False
    assert str(dish) == dish.name
    assert dish.created_at is not None
    assert dish.updated_at is not None
