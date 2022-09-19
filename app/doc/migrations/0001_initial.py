# Generated by Django 3.2.15 on 2022-09-16 14:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('folder', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=180)),
            ],
        ),
        migrations.CreateModel(
            name='Doc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(editable=False, null=True)),
                ('name', models.CharField(max_length=180)),
                ('file', models.FileField(null=True, upload_to='')),
                ('type', models.CharField(max_length=180, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('folder_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='folder.folder')),
                ('status_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='doc.status')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
