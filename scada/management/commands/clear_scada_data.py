from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection

class Command(BaseCommand):
    help = 'Clear all data from scada app tables'

    def handle(self, *args, **options):
        # Get all models from the scada app
        scada_models = [
            model for model in apps.get_models() 
            if model._meta.app_label == 'scada'
        ]
        
        # Disable foreign key checks
        with connection.cursor() as cursor:
            cursor.execute('PRAGMA foreign_keys = OFF;')
            try:
                # Delete data from each model
                for model in scada_models:
                    count = model.objects.count()
                    model.objects.all().delete()
                    self.stdout.write(
                        self.style.SUCCESS(f'Deleted {count} records from {model._meta.db_table}')
                    )
            finally:
                # Re-enable foreign key checks
                cursor.execute('PRAGMA foreign_keys = ON;')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully cleared scada app data')
        )