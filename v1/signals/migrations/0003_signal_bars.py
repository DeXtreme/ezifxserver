# Generated by Django 2.2.6 on 2019-11-02 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signals', '0002_auto_20191102_0109'),
    ]

    operations = [
        migrations.AddField(
            model_name='signal',
            name='bars',
            field=models.TextField(default='[[0.1,0.2],[0.2,0.3]]'),
            preserve_default=False,
        ),
    ]
