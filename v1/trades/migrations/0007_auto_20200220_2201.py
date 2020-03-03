# Generated by Django 2.2.6 on 2020-02-20 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trades', '0006_auto_20200205_0231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='current_price',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='trade',
            name='lot_size',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='trade',
            name='previous_price',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='trade',
            name='profit',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='trade',
            name='status',
            field=models.CharField(choices=[('O', 'Open'), ('C', 'Closed'), ('PO', 'Pending_Open'), ('PC', 'Pending_Close')], max_length=3),
        ),
        migrations.AlterField(
            model_name='trade',
            name='stoploss',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='trade',
            name='stoploss_price',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='trade',
            name='stoploss_profit',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='trade',
            name='trade_id',
            field=models.BigIntegerField(null=True),
        ),
    ]
