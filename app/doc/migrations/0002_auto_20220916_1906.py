# Generated by Django 3.2.15 on 2022-09-16 19:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='doc',
            old_name='folder_id',
            new_name='folder',
        ),
        migrations.RenameField(
            model_name='doc',
            old_name='status_id',
            new_name='status',
        ),
        migrations.RenameField(
            model_name='doc',
            old_name='user_id',
            new_name='user',
        ),
    ]
