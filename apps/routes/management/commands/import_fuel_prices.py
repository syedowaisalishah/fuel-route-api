from django.core.management.base import BaseCommand, CommandError

from apps.routes.services.fuel_station_importer import FuelStationImporter


class Command(BaseCommand):
    help = "Import fuel station pricing data from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)
        parser.add_argument("--dry-run", action="store_true", help="Parse the file without writing to the database.")

    def handle(self, *args, **options):
        file_path = options["file_path"]
        dry_run = options["dry_run"]
        importer = FuelStationImporter()

        try:
            result = importer.import_csv(file_path, dry_run=dry_run)
        except FileNotFoundError as exc:
            raise CommandError(f"File not found: {file_path}") from exc

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"Dry run complete: {result['created']} would be created, {result['updated']} would be updated"
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported fuel prices: {result['created']} created, {result['updated']} updated"
            )
        )
