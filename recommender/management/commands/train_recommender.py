from django.core.management.base import BaseCommand
from recommender.train_svd import retrain_model
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        retrain_model()

        self.stdout.write(
            self.style.SUCCESS(
                "Recommender retrain terminé"
            )
        )
