# Generated by Django 5.2.1 on 2025-06-27 11:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0002_alter_manufacturingdepartment_options_and_more'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='manufacturingdepartment',
            table='manufacturing_department',
        ),
        migrations.AlterModelTable(
            name='manufacturingmachine',
            table='manufacturing_machine',
        ),
    ]
