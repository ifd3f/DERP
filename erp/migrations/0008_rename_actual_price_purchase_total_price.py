# Generated by Django 4.2.3 on 2023-08-28 20:45

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("erp", "0007_funding_comment"),
    ]

    operations = [
        migrations.RenameField(
            model_name="purchase",
            old_name="actual_price",
            new_name="total_price",
        ),
    ]
