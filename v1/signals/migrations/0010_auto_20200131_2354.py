# Generated by Django 2.2.6 on 2020-01-31 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0009_auto_20191214_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='signal',
            name='atr',
            field=models.FloatField(default=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='signal',
            name='min_lot',
            field=models.FloatField(default=0.1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='signal',
            name='pip_value',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]
