# Generated by Django 4.2.3 on 2023-07-30 22:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("erp", "0004_alter_purchase_comment_alter_purchase_supplier"),
    ]

    operations = [
        migrations.AddField(
            model_name="purchase",
            name="create_date",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="purchase",
            name="last_update_date",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
