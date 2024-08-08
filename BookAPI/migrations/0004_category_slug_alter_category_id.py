# Generated by Django 5.0.7 on 2024-08-08 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BookAPI', '0003_alter_category_name_alter_menuitem_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(default='default-slug'),
        ),
        migrations.AlterField(
            model_name='category',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
