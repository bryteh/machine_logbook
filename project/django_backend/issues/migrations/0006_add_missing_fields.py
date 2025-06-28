# Generated manually to fix missing database fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0005_auto_20250628_0155'),
    ]

    operations = [
        # Add priority field if it doesn't exist
        migrations.RunSQL(
            "ALTER TABLE issues_issue ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium';",
            reverse_sql="ALTER TABLE issues_issue DROP COLUMN IF EXISTS priority;"
        ),
        
        # Add reported_by field if it doesn't exist
        migrations.RunSQL(
            "ALTER TABLE issues_issue ADD COLUMN IF NOT EXISTS reported_by VARCHAR(100) DEFAULT 'Unknown';",
            reverse_sql="ALTER TABLE issues_issue DROP COLUMN IF EXISTS reported_by;"
        ),
        
        # Add downtime_start field if it doesn't exist
        migrations.RunSQL(
            "ALTER TABLE issues_issue ADD COLUMN IF NOT EXISTS downtime_start TIMESTAMP NULL;",
            reverse_sql="ALTER TABLE issues_issue DROP COLUMN IF EXISTS downtime_start;"
        ),
        
        # Add downtime_end field if it doesn't exist
        migrations.RunSQL(
            "ALTER TABLE issues_issue ADD COLUMN IF NOT EXISTS downtime_end TIMESTAMP NULL;",
            reverse_sql="ALTER TABLE issues_issue DROP COLUMN IF EXISTS downtime_end;"
        ),
        
        # Drop resolved_at if it exists (old field)
        migrations.RunSQL(
            "ALTER TABLE issues_issue DROP COLUMN IF EXISTS resolved_at;",
            reverse_sql="ALTER TABLE issues_issue ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP NULL;"
        ),
        
        # Add any other missing fields for remedies table
        migrations.RunSQL(
            "ALTER TABLE issues_remedy ADD COLUMN IF NOT EXISTS parts_purchased TEXT DEFAULT '';",
            reverse_sql="ALTER TABLE issues_remedy DROP COLUMN IF EXISTS parts_purchased;"
        ),
        
        migrations.RunSQL(
            "ALTER TABLE issues_remedy ADD COLUMN IF NOT EXISTS labor_cost DECIMAL(10,2) NULL;",
            reverse_sql="ALTER TABLE issues_remedy DROP COLUMN IF EXISTS labor_cost;"
        ),
        
        migrations.RunSQL(
            "ALTER TABLE issues_remedy ADD COLUMN IF NOT EXISTS parts_cost DECIMAL(10,2) NULL;",
            reverse_sql="ALTER TABLE issues_remedy DROP COLUMN IF EXISTS parts_cost;"
        ),
        
        migrations.RunSQL(
            "ALTER TABLE issues_remedy ADD COLUMN IF NOT EXISTS total_cost DECIMAL(10,2) NULL;",
            reverse_sql="ALTER TABLE issues_remedy DROP COLUMN IF EXISTS total_cost;"
        ),
        
        migrations.RunSQL(
            "ALTER TABLE issues_remedy ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
            reverse_sql="ALTER TABLE issues_remedy DROP COLUMN IF EXISTS updated_at;"
        ),
    ] 