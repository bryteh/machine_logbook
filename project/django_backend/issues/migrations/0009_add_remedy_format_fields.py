# Generated manually to add format guide fields to Remedy model

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0008_add_updated_at_field'),
    ]

    operations = [
        # Add problem_format_guide field
        migrations.RunSQL(
            "ALTER TABLE issues_remedy ADD COLUMN IF NOT EXISTS problem_format_guide TEXT DEFAULT 'Problem Description Guide';",
            reverse_sql="ALTER TABLE issues_remedy DROP COLUMN IF EXISTS problem_format_guide;"
        ),
        
        # Add remedy_format_guide field  
        migrations.RunSQL(
            "ALTER TABLE issues_remedy ADD COLUMN IF NOT EXISTS remedy_format_guide TEXT DEFAULT 'Remedy Description Guide';",
            reverse_sql="ALTER TABLE issues_remedy DROP COLUMN IF EXISTS remedy_format_guide;"
        ),
    ] 