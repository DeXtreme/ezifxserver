# Generated by Django 2.2.6 on 2020-02-26 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0011_remove_signal_pip_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signal',
            name='timeframe',
            field=models.CharField(choices=[('D1', '1Day'), ('H4', '4Hour'), ('H1', '1Hour'), ('M30', '30Minutes')], max_length=4),
        ),
    ]
