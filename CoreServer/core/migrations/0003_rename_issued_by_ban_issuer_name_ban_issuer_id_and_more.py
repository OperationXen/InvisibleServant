# Generated by Django 4.0.1 on 2022-01-15 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_rank_strike_alter_dm_options_alter_ban_datetime_end_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ban',
            old_name='issued_by',
            new_name='issuer_name',
        ),
        migrations.AddField(
            model_name='ban',
            name='issuer_id',
            field=models.IntegerField(blank=True, help_text='Discord ID of issuing admin', null=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='datetime',
            field=models.DateTimeField(help_text='Date/Time game is starting (your local time)'),
        ),
        migrations.AlterField(
            model_name='game',
            name='datetime_open_release',
            field=models.DateTimeField(blank=True, help_text='Date/Time game is released to gen-pop (your local time)', null=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='datetime_release',
            field=models.DateTimeField(blank=True, help_text='Date/Time game is released for signups (your local time)', null=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='status',
            field=models.TextField(choices=[('Cancelled', 'Cancelled'), ('Draft', 'Draft'), ('Pending', 'Pending release'), ('Priority', 'Released to priority queue'), ('Released', 'Released to everyone')], default='Draft', help_text='Game status', max_length=16),
        ),
    ]
