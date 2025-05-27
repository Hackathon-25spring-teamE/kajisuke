from django.db import migrations


def load_initial_data(apps, schema_editor):
    MyModel = apps.get_model("apps", "MyModel")
    if not MyModel.objects.filter(name="default").exists():
        MyModel.objects.create(name="default")


class Migration(migrations.Migration):
    dependencies = [
        ("apps", "0003_initial"),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ]