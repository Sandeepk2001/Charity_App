# Generated by Django 3.2.7 on 2023-02-27 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0022_blood'),
    ]

    operations = [
        migrations.AddField(
            model_name='blood',
            name='address',
            field=models.CharField(default='', max_length=50000),
        ),
    ]
