"""
Views for the menu API.
"""

from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from menu.models import Dish, Menu
from menu.serializers import (
    DishImageSerializer,
    DishSerializer,
    MenuDetailSerializer,
    MenuSerializer,
)


class MenuViewSet(viewsets.ModelViewSet):
    """View for managing menu APIs."""

    serializer_class = MenuSerializer
    queryset = Menu.objects.annotate(dishes_count=Count("dishes")).prefetch_related("dishes").order_by("id")
    permission_classes = (IsAuthenticatedOrReadOnly,)

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_fields = (
        "name",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "description",
    )
    ordering_fields = (
        "name",
        "dishes_count",
        "created_at",
    )

    def get_queryset(self):
        """Extend queryset to handle custom logic."""
        queryset = self.queryset

        # If the user is anonymous, we only show menus with dishes
        if self.request.user.is_anonymous:
            queryset = queryset.filter(dishes__isnull=False).distinct()

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == "retrieve":
            return MenuDetailSerializer
        return self.serializer_class


class DishViewSet(viewsets.ModelViewSet):
    """View for managing dish APIs."""

    serializer_class = DishSerializer
    queryset = Dish.objects.all().order_by("id")
    permission_classes = (IsAuthenticatedOrReadOnly,)

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )
    filterset_fields = (
        "menu",
        "is_vegetarian",
    )
    search_fields = ("name", "description")

    def get_serializer_class(self):
        """Return appropriate serializer class for request."""
        if self.action == "upload_image":
            return DishImageSerializer
        return self.serializer_class

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload an image to a dish."""
        dish = self.get_object()
        serializer = self.get_serializer(dish, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
