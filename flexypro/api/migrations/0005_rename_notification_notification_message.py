# Generated by Django 4.2.7 on 2023-11-30 14:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_notification_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='notification',
            new_name='message',
        ),
    ]