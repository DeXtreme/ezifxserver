# Generated by Django 2.2.6 on 2019-12-14 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0008_auto_20191109_1734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signalgenerator',
            name='generator_type',
            field=models.CharField(choices=[('RG', 'Regular'), ('PR', 'Premium')], default='R', max_length=5),
        ),
    ]
