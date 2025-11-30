"""
Celery tasks for the menu app.
"""

from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mass_mail
from django.utils import timezone

from menu.models import Dish


@shared_task
def send_daily_menu_report():
    """
    Sends a daily email report to all users about dishes created or modified yesterday.
    This task is scheduled to run daily at 10:00 AM.
    """
    now = timezone.now()
    yesterday = now - timedelta(days=1)
    yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

    new_dishes = Dish.objects.filter(created_at__range=(yesterday_start, yesterday_end))

    modified_dishes = Dish.objects.filter(updated_at__range=(yesterday_start, yesterday_end)).exclude(
        id__in=new_dishes.values("id")
    )

    if not new_dishes.exists() and not modified_dishes.exists():
        return "No updates yesterday. No emails sent."

    subject = f"eMenu Daily Report - {yesterday.date()}"
    message_lines = ["Here is the summary of menu updates from yesterday:\n"]

    if new_dishes.exists():
        message_lines.append("NEW DISHES:")
        for dish in new_dishes:
            message_lines.append(f"- {dish.name} (${dish.price}) in {dish.menu.name}")
        message_lines.append("")

    if modified_dishes.exists():
        message_lines.append("MODIFIED DISHES:")
        for dish in modified_dishes:
            message_lines.append(f"- {dish.name} (${dish.price})")
        message_lines.append("")

    message_lines.append("\nCheck them out in the app!")
    full_message = "\n".join(message_lines)

    users = get_user_model().objects.filter(is_active=True)
    recipient_list = list(users.values_list("email", flat=True))

    if not recipient_list:
        return "No active users found."

    email_from = "no-reply@emenu.com"
    datatuple = ((subject, full_message, email_from, [email]) for email in recipient_list)

    sent_count = send_mass_mail(datatuple, fail_silently=False)

    return f"Sent {sent_count} emails."
