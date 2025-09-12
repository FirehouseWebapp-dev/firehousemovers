# Generated manually to ensure database constraint exists
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("evaluation", "0016_alter_dynamicmanagerevaluation_unique_together"),
    ]

    operations = [
        # Create a unique partial index to enforce the business rule
        # Only one active EvalForm can exist for each (department, name)
        migrations.RunSQL(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_evalform_one_active_per_dept_per_type 
            ON evaluation_evalform (department_id, name) 
            WHERE is_active = true;
            """,
            reverse_sql="DROP INDEX IF EXISTS uq_evalform_one_active_per_dept_per_type;"
        ),
    ]
