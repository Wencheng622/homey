# Generated manually for AdminInvitation model

import uuid

import django.db.models.deletion
import users.models
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_user_status_email_unverified"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdminInvitation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("email", models.EmailField(max_length=254)),
                (
                    "email_normalized",
                    models.CharField(db_index=True, editable=False, max_length=254),
                ),
                (
                    "token",
                    models.CharField(
                        default=users.models.generate_invitation_token,
                        editable=False,
                        max_length=64,
                        unique=True,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("accepted", "Accepted"),
                            ("rejected", "Rejected"),
                            ("expired", "Expired"),
                            ("revoked", "Revoked"),
                        ],
                        db_index=True,
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("expires_at", models.DateTimeField()),
                ("accepted_at", models.DateTimeField(blank=True, null=True)),
                ("rejected_at", models.DateTimeField(blank=True, null=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "accepted_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="admin_invitations_accepted",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="admin_invitations_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "admin invitation",
                "verbose_name_plural": "admin invitations",
                "db_table": "admin_invitations",
            },
        ),
        migrations.AddIndex(
            model_name="admininvitation",
            index=models.Index(fields=["email"], name="admin_invit_email_8a1f2d_idx"),
        ),
        migrations.AddIndex(
            model_name="admininvitation",
            index=models.Index(fields=["email_normalized"], name="admin_invit_email_n_4c8e91_idx"),
        ),
        migrations.AddIndex(
            model_name="admininvitation",
            index=models.Index(fields=["token"], name="admin_invit_token_2b7f04_idx"),
        ),
        migrations.AddIndex(
            model_name="admininvitation",
            index=models.Index(fields=["status"], name="admin_invit_status_9d3a12_idx"),
        ),
        migrations.AddIndex(
            model_name="admininvitation",
            index=models.Index(fields=["created_by"], name="admin_invit_created_1e5f88_idx"),
        ),
        migrations.AddIndex(
            model_name="admininvitation",
            index=models.Index(fields=["accepted_user"], name="admin_invit_accepte_6a2c47_idx"),
        ),
        migrations.AddIndex(
            model_name="admininvitation",
            index=models.Index(
                fields=["email_normalized", "status"],
                name="admin_invit_email_n_7b3d20_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="admininvitation",
            constraint=models.CheckConstraint(
                condition=Q(
                    status__in=["pending", "accepted", "rejected", "expired", "revoked"],
                ),
                name="users_admininvitation_status_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="admininvitation",
            constraint=models.UniqueConstraint(
                condition=Q(("status", "pending")),
                fields=("email_normalized",),
                name="users_admininvitation_one_pending_per_email",
            ),
        ),
    ]
