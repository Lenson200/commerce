# Generated by Django 5.1.2 on 2024-10-23 13:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0019_watchlist"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Watchlist",
        ),
    ]