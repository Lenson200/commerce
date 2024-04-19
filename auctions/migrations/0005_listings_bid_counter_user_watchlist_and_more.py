# Generated by Django 4.2.6 on 2024-04-02 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_auto_20240403_0121'),
    ]

    operations = [
        migrations.AddField(
            model_name='listings',
            name='bid_counter',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='user',
            name='watchlist',
            field=models.ManyToManyField(blank=True, related_name='watchlist', to='auctions.listings'),
        ),
        migrations.AddField(
            model_name='user',
            name='watchlist_counter',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]