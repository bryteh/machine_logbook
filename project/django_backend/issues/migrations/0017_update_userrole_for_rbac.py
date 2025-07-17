# Create UserRole table with new RBAC structure

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('issues', '0016_create_flexible_rbac_system'),
    ]

    operations = [
        # Create UserRole model with the new structure
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission_overrides', models.JSONField(blank=True, default=dict, help_text='Individual permission overrides: {permission_codename: true/false}')),
                ('can_view_costs', models.BooleanField(default=False)),
                ('can_view_external_contacts', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='issues.role')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='role', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ] 