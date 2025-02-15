# Generated by Django 5.1.1 on 2024-11-03 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_lottery_remove_credit_core_credit_owner_i_c3fcbb_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='signup_type',
            field=models.TextField(choices=[('default', 'First come first served with waitlist'), ('lottery', 'Lottery mode with random player selection')], default='default', help_text='The signup flow that will be used for this game', max_length=16),
        ),
    ]
