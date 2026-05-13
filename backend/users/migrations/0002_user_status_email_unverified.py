# Generated manually for email_unverified status and constraint updates

from django.db import migrations, models
from django.db.models import Q


def forwards_pending_to_email_unverified(apps, schema_editor):
    User = apps.get_model("users", "User")
    User.objects.filter(status="pending_verification").update(status="email_unverified")


def reverse_email_unverified_to_pending(apps, schema_editor):
    User = apps.get_model("users", "User")
    User.objects.filter(status="email_unverified").update(status="pending_verification")


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="user",
            name="users_user_status_valid",
        ),
        migrations.RemoveConstraint(
            model_name="user",
            name="users_user_email_verified_status_consistency",
        ),
        migrations.RunPython(
            forwards_pending_to_email_unverified,
            reverse_email_unverified_to_pending,
        ),
        migrations.AlterField(
            model_name="user",
            name="status",
            field=models.CharField(
                choices=[
                    ("email_unverified", "Email unverified"),
                    ("active", "Active"),
                    ("suspended", "Suspended"),
                    ("deleted", "Deleted"),
                ],
                default="email_unverified",
                max_length=32,
            ),
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.CheckConstraint(
                condition=Q(
                    status__in=["email_unverified", "active", "suspended", "deleted"],
                ),
                name="users_user_status_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.CheckConstraint(
                condition=~Q(is_email_verified=True, status="email_unverified"),
                name="users_user_email_verified_status_consistency",
            ),
        ),
    ]
