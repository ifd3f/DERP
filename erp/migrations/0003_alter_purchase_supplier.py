# Generated by Django 4.2.3 on 2023-07-28 15:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("erp", "0002_purchase_comment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="purchase",
            name="supplier",
            field=models.URLField(null=True),
        ),
    ]
