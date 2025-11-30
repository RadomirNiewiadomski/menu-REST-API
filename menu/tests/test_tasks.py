"""
Tests for Celery tasks.
"""

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from menu.models import Dish, Menu
from menu.tasks import send_daily_menu_report


@pytest.mark.django_db
class TestReportingTask:
    """Test the daily reporting task."""

    def test_task_sends_email_with_updates(self):
        """Test that email is sent when there are new/modified dishes."""
        User = get_user_model()
        User.objects.create_user("u1@example.com", "pass")
        User.objects.create_user("u2@example.com", "pass")

        menu = Menu.objects.create(name="Menu", description="Desc")

        now = timezone.now()
        yesterday = now - timedelta(days=1)

        dish_new = Dish.objects.create(menu=menu, name="New Dish", price=Decimal("10.00"), prep_time=10)
        Dish.objects.filter(id=dish_new.id).update(created_at=yesterday)

        day_before = now - timedelta(days=2)
        dish_mod = Dish.objects.create(menu=menu, name="Mod Dish", price=Decimal("20.00"), prep_time=20)
        Dish.objects.filter(id=dish_mod.id).update(created_at=day_before, updated_at=yesterday)

        dish_old = Dish.objects.create(menu=menu, name="Old Dish", price=Decimal("5.00"), prep_time=5)
        Dish.objects.filter(id=dish_old.id).update(created_at=day_before, updated_at=day_before)

        with patch("menu.tasks.send_mass_mail") as mock_send:
            mock_send.return_value = 2

            result = send_daily_menu_report()

            assert "Sent 2 emails" in result
            assert mock_send.called

            call_args = mock_send.call_args[0][0]
            messages = list(call_args)

            assert len(messages) == 2

            subject, body, _, _ = messages[0]

            assert "eMenu Daily Report" in subject
            assert "New Dish" in body
            assert "Mod Dish" in body
            assert "Old Dish" not in body

    def test_task_sends_no_email_if_no_changes(self):
        """Test that no email is sent if nothing changed yesterday."""
        User = get_user_model()
        User.objects.create_user("u1@example.com", "pass")

        with patch("menu.tasks.send_mass_mail") as mock_send:
            result = send_daily_menu_report()

            assert "No updates" in result
            assert mock_send.called is False
