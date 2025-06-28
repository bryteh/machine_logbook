# Generated manually to add reported_by field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0006_add_missing_fields'),
    ]

    operations = [
        # Add reported_by field if it doesn't exist
        migrations.RunSQL(
            "ALTER TABLE issues_issue ADD COLUMN IF NOT EXISTS reported_by VARCHAR(100) DEFAULT 'Unknown';",
            reverse_sql="ALTER TABLE issues_issue DROP COLUMN IF EXISTS reported_by;"
        ),
    ] 