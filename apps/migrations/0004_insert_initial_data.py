import json
from django.core.management import call_command
from django.db import migrations


def load_initial_data(apps, schema_editor):
    call_command("loaddata", "initial_data.json")


class Migration(migrations.Migration):
    dependencies = [
        ("apps", "0003_remove_schedule_day_of_month"),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ]