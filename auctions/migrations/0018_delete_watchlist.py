# Generated by Django 5.1.2 on 2024-10-23 13:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0017_comment"),
    ]

    operations = [
        migrations.DeleteModel(
            name="WatchList",
        ),
    ]
