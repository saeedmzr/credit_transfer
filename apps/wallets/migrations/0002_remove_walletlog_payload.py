# Generated by Django 4.2.9 on 2024-10-16 16:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='walletlog',
            name='payload',
        ),
    ]
