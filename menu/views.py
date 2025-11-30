"""
Views for the menu API.
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from menu.models import Menu
from menu.serializers import MenuDetailSerializer, MenuSerializer


class MenuViewSet(viewsets.ModelViewSet):
    """View for managing menu APIs."""

    serializer_class = MenuSerializer
    queryset = Menu.objects.all().order_by("id")
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == "retrieve":
            return MenuDetailSerializer
        return self.serializer_class
