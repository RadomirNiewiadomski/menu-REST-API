"""
Serializers for the menu API.
"""

from rest_framework import serializers

from menu.models import Menu


class MenuSerializer(serializers.ModelSerializer):
    """Serializer for the Menu object."""

    class Meta:
        model = Menu
        fields = (
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class MenuDetailSerializer(MenuSerializer):
    """Serializer for the Menu Detail object."""

    # Tu w przyszłości dodam listę dań:
    # dishes = DishSerializer(many=True, read_only=True)

    class Meta(MenuSerializer.Meta):
        pass
