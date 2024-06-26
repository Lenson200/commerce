# Generated by Django 4.2.6 on 2024-04-02 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='listings',
            fields=[
                ('uniqueid', models.IntegerField(auto_created=True, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=255)),
                ('startingbid', models.IntegerField()),
                ('currentprice', models.IntegerField()),
                ('category', models.CharField(max_length=64)),
                ('imageurl', models.CharField(max_length=255)),
            ],
        ),
    ]
