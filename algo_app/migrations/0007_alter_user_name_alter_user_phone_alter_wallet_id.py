# Generated by Django 4.2.7 on 2025-06-23 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('algo_app', '0006_remove_wallet_amount_user_is_email_verified_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(default='', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(db_index=True, default='', max_length=50, null=True, unique=True),
        ),
    ]
