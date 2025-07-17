# Generated manually for AuditLog model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('issues', '0018_auto_20250702_0217'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action', models.CharField(choices=[('issue_created', 'Issue Created'), ('issue_updated', 'Issue Updated'), ('issue_resolved', 'Issue Resolved'), ('issue_reopened', 'Issue Reopened'), ('remedy_added', 'Remedy Added'), ('remedy_updated', 'Remedy Updated'), ('remedy_deleted', 'Remedy Deleted'), ('report_generated', 'Report Generated'), ('status_changed', 'Status Changed'), ('attachment_added', 'Attachment Added'), ('attachment_deleted', 'Attachment Deleted'), ('user_login', 'User Login'), ('user_logout', 'User Logout'), ('permission_changed', 'Permission Changed'), ('other', 'Other')], max_length=50)),
                ('description', models.TextField()),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('issue', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='issues.issue')),
                ('remedy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='issues.remedy')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['user', '-created_at'], name='issues_audi_user_id_a6b5f3_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['action', '-created_at'], name='issues_audi_action_a91d5e_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['issue', '-created_at'], name='issues_audi_issue_i_7e9c2a_idx'),
        ),
    ] 