"""
Tests for the Django admin.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.fixture
def admin_user():
    """Fixture creating an admin user."""
    return User.objects.create_superuser(email="admin@example.com", password="password123", name="Admin User")


@pytest.fixture
def regular_user():
    """Fixture creating a regular user."""
    return User.objects.create_user(email="user@example.com", password="password123", name="Test User")


@pytest.mark.django_db
def test_users_list(client, admin_user, regular_user):
    """Test that users are listed on page"""
    url = reverse("admin:user_user_changelist")
    client.force_login(admin_user)
    response = client.get(url)

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert regular_user.name in content
    assert regular_user.email in content


@pytest.mark.django_db
def test_edit_user_page(client, admin_user, regular_user):
    """Test that users can be edited"""
    url = reverse("admin:user_user_change", args=[regular_user.id])
    client.force_login(admin_user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_user_page(client, admin_user):
    """Test that users can be created"""
    url = reverse("admin:user_user_add")
    client.force_login(admin_user)
    response = client.get(url)
    assert response.status_code == 200
