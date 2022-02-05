# Generated by Django 4.0 on 2022-02-05 22:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_ban_issuer_id_alter_ban_issuer_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BonusCredit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discord_id', models.IntegerField(blank=True, help_text='Discord ID of player', null=True)),
                ('discord_name', models.CharField(blank=True, help_text='Player name to receive bonus game credits', max_length=32)),
                ('credits', models.IntegerField(default=1, help_text='Number of additional credits', verbose_name='Number of bonus games')),
                ('expires', models.DateTimeField(blank=True, help_text='Date that these credits expire', null=True, verbose_name='Expiry date (optional)')),
                ('issuer_id', models.IntegerField(blank=True, help_text='Discord ID of issuing moderator', null=True)),
                ('issuer_name', models.CharField(help_text='Name of the issuing moderator', max_length=32)),
                ('reason', models.TextField(blank=True, help_text='The reason that these games have been awarded', null=True)),
            ],
        ),
        migrations.AddIndex(
            model_name='bonuscredit',
            index=models.Index(fields=['discord_id', 'expires'], name='core_bonusc_discord_55d16f_idx'),
        ),
    ]
