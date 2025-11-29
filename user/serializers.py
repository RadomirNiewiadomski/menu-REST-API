"""
Serializers for the user API View.
"""

from typing import Any, ClassVar

from django.contrib.auth import get_user_model
from rest_framework import serializers

from user.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ("email", "password", "name")
        extra_kwargs: ClassVar[dict[str, Any]] = {
            "password": {
                "write_only": True,
                "min_length": 5,
            }
        }

    def create(self, validated_data: dict[str, Any]) -> User:
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        """Update and return user."""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
