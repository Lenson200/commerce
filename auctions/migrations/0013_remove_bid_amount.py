# Generated by Django 4.2.6 on 2024-04-11 21:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_all_listings_active_all_listings_winner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bid',
            name='amount',
        ),
    ]
