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

    def test_imports_assessment_csv_headers(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as handle:
            handle.write(
                "OPIS Truckstop ID,Truckstop Name,Address,City,State,Rack ID,Retail Price\n"
                '7,WOODSHED OF BIG CABIN,"I-44, EXIT 283 & US-69",Big Cabin,OK,307,3.00733333\n'
            )
            file_path = handle.name

        try:
            call_command("import_fuel_prices", file_path)
            station = FuelStation.objects.get()
            self.assertEqual(station.name, "WOODSHED OF BIG CABIN")
            self.assertEqual(station.city, "Big Cabin")
            self.assertEqual(station.state, "OK")
            self.assertEqual(str(station.price_per_gallon), "3.007")
        finally:
            unlink(file_path)
