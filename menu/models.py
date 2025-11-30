"""
Database models for the Menu app.
"""

import uuid
from pathlib import Path

from django.db import models
from django.utils.translation import gettext_lazy as _


def dish_image_file_path(instance: "Dish", filename: str) -> str:
    """Generate file path for new dish image."""
    ext = Path(filename).suffix
    filename = f"{uuid.uuid4()}{ext}"
    return str(Path("uploads") / "dish" / filename)


class Menu(models.Model):
    """Menu object representing a card of dishes."""

    name = models.CharField(_("name"), max_length=255, unique=True)
    description = models.TextField(_("description"), blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("menu")
        verbose_name_plural = _("menus")

    def __str__(self) -> str:
        return self.name


class Dish(models.Model):
    """Dish object for the menu."""

    menu = models.ForeignKey(
        Menu,
        related_name="dishes",
        on_delete=models.CASCADE,
        verbose_name=_("menu"),
    )
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    price = models.DecimalField(_("price"), max_digits=10, decimal_places=2)
    prep_time = models.PositiveIntegerField(
        _("preparation time"),
        help_text=_("Preparation time in minutes"),
    )
    is_vegetarian = models.BooleanField(_("is vegetarian"), default=False)
    image = models.ImageField(_("image"), null=True, blank=True, upload_to=dish_image_file_path)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("dish")
        verbose_name_plural = _("dishes")

    def __str__(self) -> str:
        return self.name
