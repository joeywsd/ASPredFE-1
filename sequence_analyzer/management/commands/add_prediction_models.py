# Django core import: This provides the base class needed to build custom terminal/management commands.
from django.core.management.base import BaseCommand

# App-specific import: This pulls in your custom database Model so you can read/write data.
from sequence_analyzer.models import PredictionModel
import json
from pathlib import Path

# Django looks specifically for a class named 'Command' that inherits from 'BaseCommand'.
# The file structure matters here: this file must be inside an app under `management/commands/your_filename.py`.
class Command(BaseCommand):
    # This text shows up in the terminal if someone runs `python manage.py your_filename --help`.
    help = 'Add default prediction models to the database'

    # Django automatically calls this handle() method when the command is executed.
    # *args and **options capture any extra flags or arguments passed via the terminal.
    def handle(self, *args, **options):
        
        # A standard Python list of dictionaries containing the initial data you want to seed.
        file_path = (
            Path(__file__).resolve().parents[3]
            / "aspredINF"
            / "protein_models.json"
        )

        with file_path.open("r", encoding="utf-8") as f:
            models_data = json.load(f)

        # Loop through each model dictionary to process them one by one.
        for model_data in models_data:
            
            # DJANGO ORM MAGIC: 'get_or_create' checks the database for an entry where name=model_data["name"].
            # - If it finds it, it fetches it.
            # - If it doesn't, it creates a new entry using the fields in the 'defaults' dictionary.
            # It returns a tuple: (the database object, a boolean 'created' which is True if it's new, False if it already existed).
            obj, created = PredictionModel.objects.update_or_create(
                name=model_data["name"],
                defaults={
                    "description": model_data["description"],
                    "model_path": model_data["model_path"],
                    "is_active": True
                }
            )
            
            # Check the boolean returned by Django's get_or_create
            if created:
                # self.stdout.write ensures the output streams correctly to the terminal console.
                # self.style.SUCCESS color-codes the terminal text green.
                self.stdout.write(
                    self.style.SUCCESS(f' Created: {obj.name}')
                )
            else:
                # self.style.WARNING color-codes the terminal text olive/yellow.
                self.stdout.write(
                    self.style.SUCCESS(f' Updated: {obj.name}')
                )
                

        # Final success message printed to the console once the loop finishes completely.
        
        self.stdout.write(
            self.style.SUCCESS('✓ Prediction models setup complete!')
        )