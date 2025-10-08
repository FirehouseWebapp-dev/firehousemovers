# Generated manually on 2025-10-08
# Makes slug field required (all departments already have slugs from migration 0015)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0015_normalize_department_slugs"),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='slug',
            field=models.SlugField(
                max_length=100,
                unique=True,
                help_text="URL-friendly identifier used in dashboard links (e.g., 'drivers', 'sales')"
            ),
        ),
    ]

