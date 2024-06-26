# Generated by Django 4.2.6 on 2024-04-14 19:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0015_remove_watchlist_watchlist_watchlist_watchlist_items'),
    ]

    operations = [
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auctions.all_listings')),
            ],
        ),
    ]
