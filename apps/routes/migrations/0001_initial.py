from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FuelStation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("address", models.CharField(blank=True, max_length=255)),
                ("city", models.CharField(blank=True, max_length=128)),
                ("state", models.CharField(blank=True, max_length=32)),
                ("latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("price_per_gallon", models.DecimalField(decimal_places=3, max_digits=8)),
            ],
        ),
        migrations.AddIndex(
            model_name="fuelstation",
            index=models.Index(fields=["state", "city"], name="routes_fuel_state_2d9f8f_idx"),
        ),
        migrations.AddIndex(
            model_name="fuelstation",
            index=models.Index(fields=["price_per_gallon"], name="routes_fuel_price_37e680_idx"),
        ),
        migrations.AddConstraint(
            model_name="fuelstation",
            constraint=models.UniqueConstraint(fields=("name", "address", "city", "state"), name="unique_fuel_station_identity"),
        ),
    ]
