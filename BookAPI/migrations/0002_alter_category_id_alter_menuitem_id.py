# Generated by Django 5.0.7 on 2024-08-08 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BookAPI', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
