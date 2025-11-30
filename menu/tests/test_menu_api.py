"""
Tests for the Menu API.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from menu.models import Menu
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
        Menu.objects.create(name="Menu 1", description="Desc 1")
        res = client.get(MENU_URL)

        assert res.status_code == status.HTTP_200_OK

    def test_get_menu_detail(self, client):
        """Test get menu detail - public."""
        menu = Menu.objects.create(name="Detail Menu", description="Detail Desc")
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
