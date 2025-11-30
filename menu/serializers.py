"""
Serializers for the menu API.
"""

from rest_framework import serializers

from menu.models import Dish, Menu


class DishSerializer(serializers.ModelSerializer):
    """Serializer for dishes."""

    class Meta:
        model = Dish
        fields = (
            "id",
            "menu",
            "name",
            "description",
            "price",
            "prep_time",
            "is_vegetarian",
            "image",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class DishImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to dishes."""

    class Meta:
        model = Dish
        fields = ("id", "image")
        read_only_fields = ("id",)


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

    dishes = DishSerializer(many=True, read_only=True)

    class Meta(MenuSerializer.Meta):
        fields = (*MenuSerializer.Meta.fields, "dishes")
