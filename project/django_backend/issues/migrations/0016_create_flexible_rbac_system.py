# Generated manually for RBAC system implementation

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('issues', '0015_auto_20250701_1916'),
    ]

    operations = [
        # Create Permission model
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('codename', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('category', models.CharField(default='general', max_length=30)),
            ],
            options={
                'ordering': ['category', 'name'],
            },
        ),
        
        # Create Role model
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('codename', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_public_role', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('permissions', models.ManyToManyField(blank=True, to='issues.permission')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        
        # Create PublicRole model
        migrations.CreateModel(
            name='PublicRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('permissions', models.ManyToManyField(blank=True, to='issues.permission')),
            ],
            options={
                'verbose_name': 'Public Access Permissions',
                'verbose_name_plural': 'Public Access Permissions',
            },
        ),
        
        # Create GlobalSettings model
        migrations.CreateModel(
            name='GlobalSettings',
            fields=[
                ('id', models.BooleanField(default=True, primary_key=True, serialize=False)),
                ('max_update_text_length', models.IntegerField(default=2000)),
                ('max_attachments_per_issue', models.IntegerField(default=10)),
                ('max_attachments_per_remedy', models.IntegerField(default=5)),
                ('max_video_resolution_height', models.IntegerField(default=720)),
                ('max_video_quality_crf', models.IntegerField(default=28)),
                ('max_file_size_mb', models.IntegerField(default=50)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Global Settings',
                'verbose_name_plural': 'Global Settings',
            },
        ),
    ] 