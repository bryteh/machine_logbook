# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0009_add_remedy_format_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='remedy',
            name='is_machine_runnable',
            field=models.BooleanField(default=False, help_text='Whether machine is still runnable after remedy'),
        ),
    ] 