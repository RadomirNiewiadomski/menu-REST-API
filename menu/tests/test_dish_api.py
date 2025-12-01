"""
Tests for the Dish API.
"""

import tempfile
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from menu.models import Dish, Menu
from menu.serializers import DishSerializer
from user.models import User

DISHES_URL = reverse("menu:dish-list")


def detail_url(dish_id):
    """Return dish detail URL."""
    return reverse("menu:dish-detail", args=[dish_id])


def image_upload_url(dish_id):
    """Return URL for recipe image upload."""
    return reverse("menu:dish-upload-image", args=[dish_id])


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def user() -> User:
    return get_user_model().objects.create_user("test@example.com", "password123", name="Test User")


@pytest.fixture
def menu() -> Menu:
    """Fixture creating a menu to link dishes to."""
    return Menu.objects.create(name="Main Menu", description="Main stuff")


@pytest.mark.django_db
class TestPublicDishApi:
    """Test public dish API requests."""

    def test_auth_required(self, client):
        """Test that authentication is NOT required for retrieving dishes list."""
        res = client.get(DISHES_URL)
        assert res.status_code == status.HTTP_200_OK

    def test_get_dish_detail(self, client, menu):
        """Test get dish detail - public."""
        dish = Dish.objects.create(menu=menu, name="Detail Dish", price=Decimal("12.99"), prep_time=15)
        url = detail_url(dish.id)

        res = client.get(url)

        assert res.status_code == status.HTTP_200_OK
        assert res.data["name"] == dish.name
        assert res.data["price"] == str(dish.price)

    def test_create_dish_unauthorized(self, client, menu):
        """Test that creating dish requires authentication."""
        payload = {"menu": menu.id, "name": "New Dish", "price": "20.00", "prep_time": 10}
        res = client.post(DISHES_URL, payload)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPrivateDishApi:
    """Test authenticated dish API requests."""

    @pytest.fixture
    def auth_client(self, client, user):
        client.force_authenticate(user)
        return client

    def test_retrieve_dishes(self, auth_client, menu):
        """Test retrieving a list of dishes."""
        Dish.objects.create(menu=menu, name="Dish 1", price=Decimal("10.00"), prep_time=10)
        Dish.objects.create(menu=menu, name="Dish 2", price=Decimal("20.00"), prep_time=20)

        res = auth_client.get(DISHES_URL)

        dishes = Dish.objects.all().order_by("id")
        serializer = DishSerializer(dishes, many=True)
        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_create_dish(self, auth_client, menu):
        """Test creating a dish."""
        payload = {
            "menu": menu.id,
            "name": "Pizza",
            "price": Decimal("35.50"),
            "prep_time": 15,
            "description": "Tasty pizza",
            "is_vegetarian": True,
        }
        res = auth_client.post(DISHES_URL, payload)

        assert res.status_code == status.HTTP_201_CREATED
        dish = Dish.objects.get(id=res.data["id"])
        assert dish.name == payload["name"]
        assert dish.is_vegetarian is True
        assert dish.menu == menu

    def test_update_dish(self, auth_client, menu):
        """Test updating a dish."""
        dish = Dish.objects.create(menu=menu, name="Old Name", price=Decimal("10.00"), prep_time=10)

        payload = {
            "menu": menu.id,
            "name": "New Name",
            "price": Decimal("15.00"),
            "prep_time": 10,
        }
        url = detail_url(dish.id)
        res = auth_client.put(url, payload)

        assert res.status_code == status.HTTP_200_OK
        dish.refresh_from_db()
        assert dish.name == payload["name"]
        assert dish.price == payload["price"]

    def test_upload_image_to_dish(self, auth_client, menu):
        """Test uploading an image to dish."""
        dish = Dish.objects.create(menu=menu, name="Dish Image", price=Decimal("10.00"), prep_time=10)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)

            payload = {"image": ntf}
            url = image_upload_url(dish.id)
            res = auth_client.post(url, payload, format="multipart")

        dish.refresh_from_db()
        assert res.status_code == status.HTTP_200_OK
        assert "image" in res.data
        assert dish.image.name is not None

    def test_upload_image_bad_request(self, auth_client, menu):
        """Test uploading an invalid image."""
        dish = Dish.objects.create(menu=menu, name="Dish Image", price=Decimal("10.00"), prep_time=10)
        url = image_upload_url(dish.id)
        payload = {"image": "not an image"}
        res = auth_client.post(url, payload, format="multipart")

        assert res.status_code == status.HTTP_400_BAD_REQUEST
