# Generated by Django 4.2.7 on 2023-11-30 14:08

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_rename_user_order_client'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]