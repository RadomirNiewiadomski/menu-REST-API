"""
Tests for the user API.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token_obtain_pair")
ME_URL = reverse("user:me")


@pytest.fixture
def client() -> APIClient:
    """Fixture for APIClient."""
    return APIClient()


@pytest.mark.django_db
class TestPublicUserApi:
    """Test public features of the user API (no login required)."""

    def test_create_user_success(self, client):
        """Test creating a user with valid payload is successful."""
        payload = {"email": "test@example.com", "password": "testpass123", "name": "Test User"}
        res = client.post(CREATE_USER_URL, payload)

        assert res.status_code == status.HTTP_201_CREATED
        user = User.objects.get(email=payload["email"])
        assert user.name == payload["name"]
        assert user.check_password(payload["password"])
        assert "password" not in res.data

    def test_user_with_email_exists_error(self, client):
        """Test error returned if user with email exists."""
        email = "test@example.com"
        User.objects.create_user(email=email, password="password123")

        payload = {"email": email, "password": "newpassword123", "name": "New Name"}
        res = client.post(CREATE_USER_URL, payload)

        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_too_short_error(self, client):
        """Test error returned if password is too short."""
        payload = {
            "email": "test@example.com",
            "password": "pw",
            "name": "Test User",
        }
        res = client.post(CREATE_USER_URL, payload)

        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert User.objects.exists() is False

    def test_create_token_success(self, client):
        """Test that valid credentials return a token."""
        email = "user@example.com"
        password = "password123"
        User.objects.create_user(email=email, password=password)

        payload = {"email": email, "password": password}
        res = client.post(TOKEN_URL, payload)

        assert res.status_code == status.HTTP_200_OK
        assert "access" in res.data
        assert "refresh" in res.data

    def test_create_token_bad_credentials(self, client):
        """Test that invalid credentials return an error."""
        User.objects.create_user(email="test@example.com", password="password123")

        payload = {"email": "test@example.com", "password": "wrongpassword"}
        res = client.post(TOKEN_URL, payload)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED
        assert "access" not in res.data

    def test_me_unauthenticated(self, client):
        """Test that authentication is required for the me endpoint."""
        res = client.get(ME_URL)
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPrivateUserApi:
    """Test API requests that require authentication."""

    @pytest.fixture
    def authenticated_client(self, client):
        """Fixture that returns an authenticated client and the user."""
        user = User.objects.create_user("user@example.com", "password123", name="Test User")
        client.force_authenticate(user=user)
        return client, user

    def test_get_user_details(self, authenticated_client):
        """Test retrieving profile for authenticated user."""
        client, user = authenticated_client
        res = client.get(ME_URL)

        assert res.status_code == status.HTTP_200_OK
        assert res.data["name"] == user.name
        assert res.data["email"] == user.email
        assert "password" not in res.data

    def test_update_user_profile(self, authenticated_client):
        """Test updating the user profile for authenticated user."""
        client, user = authenticated_client
        payload = {
            "name": "New Name",
            "password": "newpassword123",
        }
        res = client.patch(ME_URL, payload)

        user.refresh_from_db()
        assert user.name == payload["name"]
        assert user.check_password(payload["password"])
        assert res.status_code == status.HTTP_200_OK

    def test_post_me_not_allowed(self, authenticated_client):
        """Test that POST is not allowed for the me endpoint."""
        client, _ = authenticated_client
        res = client.post(ME_URL, {})

        assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
