# Generated by Django 4.0 on 2022-01-28 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_remove_game_core_game_dm_id_080647_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dm',
            name='description',
            field=models.TextField(blank=True, help_text='Flavour text / details to show', null=True),
        ),
    ]
