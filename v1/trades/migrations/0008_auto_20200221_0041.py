# Generated by Django 2.2.6 on 2020-02-21 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trades', '0007_auto_20200220_2201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='status',
            field=models.CharField(choices=[('O', 'Open'), ('C', 'Closed'), ('PO', 'Pending_Open'), ('PC', 'Pending_Close'), ('A', 'Attempted')], max_length=3),
        ),
    ]
