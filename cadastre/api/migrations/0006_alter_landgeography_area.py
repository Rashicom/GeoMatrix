# Generated by Django 4.2.4 on 2023-08-29 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_landgeography_area'),
    ]

    operations = [
        migrations.AlterField(
            model_name='landgeography',
            name='area',
            field=models.FloatField(),
        ),
    ]
