# Generated by Django 5.2.3 on 2025-06-23 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
