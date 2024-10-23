# Generated by Django 5.1.2 on 2024-10-23 13:28

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0018_delete_watchlist"),
    ]

    operations = [
        migrations.CreateModel(
            name="Watchlist",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("watchlist_counter", models.IntegerField(blank=True, default=0)),
                ("added_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "listing",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="watchlists",
                        to="auctions.all_listings",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "watchlist_items",
                    models.ManyToManyField(
                        blank=True,
                        related_name="watchlist_items",
                        to="auctions.all_listings",
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "listing")},
            },
        ),
    ]
