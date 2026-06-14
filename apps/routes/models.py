from django.db import models


class FuelStation(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=128, blank=True)
    state = models.CharField(max_length=32, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    price_per_gallon = models.DecimalField(max_digits=8, decimal_places=3)

    class Meta:
        indexes = [
            models.Index(fields=["state", "city"]),
            models.Index(fields=["price_per_gallon"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["name", "address", "city", "state"], name="unique_fuel_station_identity")
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.city}, {self.state})"
