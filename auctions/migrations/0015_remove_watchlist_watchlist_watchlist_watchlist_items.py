# Generated by Django 4.2.6 on 2024-04-14 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0014_bid_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='watchlist',
            name='watchlist',
        ),
        migrations.AddField(
            model_name='watchlist',
            name='watchlist_items',
            field=models.ManyToManyField(blank=True, related_name='watchlist_items', to='auctions.all_listings'),
        ),
    ]
