from csv import DictReader
from decimal import Decimal
from pathlib import Path

from apps.routes.models import FuelStation


class FuelStationImporter:
    def import_csv(self, file_path: str, dry_run: bool = False) -> dict:
        path = Path(file_path)
        created = 0
        updated = 0

        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = DictReader(handle)
            for row in reader:
                normalized = self._normalize_row(row)
                if not normalized["name"]:
                    continue
                defaults = {
                    "address": normalized["address"],
                    "city": normalized["city"],
                    "state": normalized["state"],
                    "latitude": self._to_decimal(normalized["latitude"]),
                    "longitude": self._to_decimal(normalized["longitude"]),
                    "price_per_gallon": self._to_decimal(normalized["price_per_gallon"]),
                }
                if dry_run:
                    created += 1
                    continue

                _, was_created = FuelStation.objects.update_or_create(
                    name=normalized["name"],
                    address=normalized["address"],
                    city=normalized["city"],
                    state=normalized["state"],
                    defaults=defaults,
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

        return {"created": created, "updated": updated}

    def _normalize_row(self, row: dict) -> dict:
        def pick(*keys: str) -> str:
            for key in keys:
                value = row.get(key)
                if value not in (None, ""):
                    return str(value).strip()
            return ""

        return {
            "name": pick("name", "station_name", "brand"),
            "address": pick("address", "street", "street_address"),
            "city": pick("city", "town"),
            "state": pick("state", "region"),
            "latitude": pick("latitude", "lat"),
            "longitude": pick("longitude", "lng", "lon", "long"),
            "price_per_gallon": pick("price_per_gallon", "price", "gas_price"),
        }

    def _to_decimal(self, value):
        if value in (None, ""):
            return None
        return Decimal(str(value).strip())
