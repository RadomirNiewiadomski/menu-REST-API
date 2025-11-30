"""
Tests for the Menu API.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from menu.models import Dish, Menu
from menu.serializers import MenuSerializer

MENU_URL = reverse("menu:menu-list")


def detail_url(menu_id: int) -> str:
    """Return menu detail URL."""
    return reverse("menu:menu-detail", args=[menu_id])


@pytest.fixture
def client() -> APIClient:
    """Fixture for APIClient."""
    return APIClient()


@pytest.fixture
def user() -> get_user_model():
    """Fixture for creating a test user."""
    return get_user_model().objects.create_user(
        "test@example.com",
        "testpass123",
        name="Test User",
    )


@pytest.mark.django_db
class TestPublicMenuApi:
    """Test the public features of the Menu API (unauthenticated)."""

    def test_retrieve_menus_public(self, client):
        """Test that authentication is NOT required for retrieving menus list."""
        menu = Menu.objects.create(name="Menu 1", description="Desc 1")
        Dish.objects.create(menu=menu, name="D1", price=10, prep_time=5)

        res = client.get(MENU_URL)

        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 1

    def test_get_menu_detail(self, client):
        """Test get menu detail - public."""
        menu = Menu.objects.create(name="Detail Menu", description="Detail Desc")
        Dish.objects.create(menu=menu, name="D1", price=10, prep_time=5)

        url = detail_url(menu.id)

        res = client.get(url)

        assert res.status_code == status.HTTP_200_OK
        assert res.data["name"] == menu.name
        assert res.data["description"] == menu.description

    def test_create_menu_unauthorized(self, client):
        """Test that creating menu requires authentication."""
        payload = {"name": "New Menu"}
        res = client.post(MENU_URL, payload)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_menus_filtered_by_name(self, client):
        """Test filtering menus by name."""
        m1 = Menu.objects.create(name="Vegetarian", description="No meat")
        Dish.objects.create(menu=m1, name="D1", price=10, prep_time=5)

        m2 = Menu.objects.create(name="Carnivore", description="Meat only")
        Dish.objects.create(menu=m2, name="D2", price=10, prep_time=5)

        res = client.get(MENU_URL, {"name": "Vegetarian"})

        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 1
        assert res.data[0]["name"] == m1.name
        assert m2.id != res.data[0]["id"]

    def test_retrieve_menus_search(self, client):
        """Test searching menus."""
        m1 = Menu.objects.create(name="Lunch Special", description="Cheap")
        Dish.objects.create(menu=m1, name="D1", price=10, prep_time=5)

        m2 = Menu.objects.create(name="Dinner Deluxe", description="Expensive")
        Dish.objects.create(menu=m2, name="D2", price=10, prep_time=5)

        res = client.get(MENU_URL, {"search": "Lunch"})

        assert len(res.data) == 1
        assert res.data[0]["name"] == m1.name
        assert m2.name != res.data[0]["name"]

    def test_sort_menus_by_dishes_count(self, client):
        """Test sorting menus by number of dishes."""
        m_less = Menu.objects.create(name="Less")
        Dish.objects.create(menu=m_less, name="D1", price=10, prep_time=5)

        m_more = Menu.objects.create(name="More")
        Dish.objects.create(menu=m_more, name="D1", price=10, prep_time=5)
        Dish.objects.create(menu=m_more, name="D2", price=10, prep_time=5)

        res = client.get(MENU_URL, {"ordering": "-dishes_count"})

        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 2
        assert res.data[0]["name"] == m_more.name
        assert res.data[1]["name"] == m_less.name

    def test_list_menus_only_non_empty_by_default(self, client):
        """Test listing only non-empty menus by default for public users."""
        m_empty = Menu.objects.create(name="Empty")
        m_full = Menu.objects.create(name="Full")
        Dish.objects.create(menu=m_full, name="D1", price=10, prep_time=5)

        res = client.get(MENU_URL)

        assert len(res.data) == 1
        assert res.data[0]["name"] == m_full.name
        assert m_empty.name != res.data[0]["name"]


@pytest.mark.django_db
class TestPrivateMenuApi:
    """Test the private features of the Menu API (authenticated)."""

    @pytest.fixture
    def auth_client(self, client, user):
        """Fixture for an authenticated client."""
        client.force_authenticate(user)
        return client

    def test_retrieve_menus(self, auth_client):
        """Test retrieving a list of menus."""
        Menu.objects.create(name="Menu 1", description="Desc 1")
        Menu.objects.create(name="Menu 2", description="Desc 2")

        res = auth_client.get(MENU_URL)

        menus = Menu.objects.all().order_by("id")
        serializer = MenuSerializer(menus, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_create_menu(self, auth_client):
        """Test creating a menu."""
        payload = {
            "name": "Summer Menu",
            "description": "Fresh summer dishes.",
        }
        res = auth_client.post(MENU_URL, payload)

        assert res.status_code == status.HTTP_201_CREATED
        menu = Menu.objects.get(id=res.data["id"])
        assert menu.name == payload["name"]
        assert menu.description == payload["description"]

    def test_update_menu(self, auth_client):
        """Test updating a menu."""
        menu = Menu.objects.create(name="Old Name", description="Old Desc")

        payload = {
            "name": "New Name",
            "description": "New Desc",
        }
        url = detail_url(menu.id)
        res = auth_client.put(url, payload)

        assert res.status_code == status.HTTP_200_OK
        menu.refresh_from_db()
        assert menu.name == payload["name"]
        assert menu.description == payload["description"]

    def test_delete_menu(self, auth_client):
        """Test deleting a menu."""
        menu = Menu.objects.create(name="To Delete", description="...")

        url = detail_url(menu.id)
        res = auth_client.delete(url)

        assert res.status_code == status.HTTP_204_NO_CONTENT
        assert Menu.objects.filter(id=menu.id).exists() is False

    def test_retrieve_all_menus_including_empty(self, auth_client):
        """Test retrieving all menus (even empty ones) for authenticated users."""
        m_empty = Menu.objects.create(name="Empty")
        m_full = Menu.objects.create(name="Full")
        Dish.objects.create(menu=m_full, name="D1", price=10, prep_time=5)

        res = auth_client.get(MENU_URL)

        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 2
        names = [menu["name"] for menu in res.data]
        assert m_empty.name in names
        assert m_full.name in names
