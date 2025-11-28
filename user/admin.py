"""Django admin configuration for the User app."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""

    ordering = ("id",)  # Przecinek ważny przy jednym elemencie!
    list_display = ("email", "name", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff")
    search_fields = ("email", "name")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("name",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password", "name", "is_staff"),
            },
        ),
    )


admin.site.register(User, UserAdmin)
