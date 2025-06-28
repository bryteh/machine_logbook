# Generated manually to add updated_at field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0007_add_reported_by_field'),
    ]

    operations = [
        # Add updated_at field if it doesn't exist
        migrations.RunSQL(
            "ALTER TABLE issues_issue ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
            reverse_sql="ALTER TABLE issues_issue DROP COLUMN IF EXISTS updated_at;"
        ),
    ] 