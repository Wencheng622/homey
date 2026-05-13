from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import Profile, User


@receiver(post_save, sender=User)
def ensure_user_profile(sender, instance: User, created: bool, **kwargs) -> None:
    """Ensure every user has exactly one profile row (integrity across all creation paths)."""
    Profile.objects.get_or_create(
        user=instance,
        defaults={},
    )
