import tempfile
from os import unlink

from django.core.management import call_command
from django.test import TestCase

from apps.routes.models import FuelStation


class FuelStationImporterTests(TestCase):
    def test_imports_common_csv_headers(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as handle:
            handle.write(
                "station_name,address,city,state,lat,lon,price\n"
                "Fuel One,123 Main St,Austin,TX,30.26,-97.74,3.49\n"
                "Fuel Two,456 Oak St,Dallas,TX,32.78,-96.80,3.29\n"
            )
            file_path = handle.name

        try:
            call_command("import_fuel_prices", file_path, "--dry-run")
            self.assertEqual(FuelStation.objects.count(), 0)
        finally:
            unlink(file_path)
