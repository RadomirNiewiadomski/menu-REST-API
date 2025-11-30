"""
Django admin configuration for the Menu app.
"""

from django.contrib import admin

from menu import models


@admin.register(models.Menu)
class MenuAdmin(admin.ModelAdmin):
    """Admin configuration for Menu model."""

    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(models.Dish)
class DishAdmin(admin.ModelAdmin):
    """Admin configuration for Dish model."""

    list_display = ("name", "menu", "price", "is_vegetarian", "created_at")
    list_filter = ("is_vegetarian", "menu")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")
