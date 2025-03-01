# Generated by Django 5.0.7 on 2024-08-08 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BookAPI', '0004_category_slug_alter_category_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='name',
            new_name='title',
        ),
        migrations.AddField(
            model_name='menuitem',
            name='inventory',
            field=models.SmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(),
        ),
    ]
