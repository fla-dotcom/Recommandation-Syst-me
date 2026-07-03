from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Interaction


@receiver(post_save, sender=Interaction)
@receiver(post_delete, sender=Interaction)
def clear_cache_on_interaction_change(sender, **kwargs):
    pass