# Generated manually to ensure database constraint exists
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("evaluation", "0016_alter_dynamicmanagerevaluation_unique_together"),
    ]

    operations = [
        # Ensure the unique constraint exists and is properly enforced
        migrations.RunSQL(
            # SQL to create the constraint if it doesn't exist
            """
            DO $$
            BEGIN
                -- Check if constraint already exists
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint 
                    WHERE conname = 'uq_evalform_one_active_per_dept_per_type'
                ) THEN
                    -- Create the unique constraint
                    ALTER TABLE evaluation_evalform 
                    ADD CONSTRAINT uq_evalform_one_active_per_dept_per_type 
                    UNIQUE (department_id, name) 
                    WHERE is_active = true;
                END IF;
            END $$;
            """,
            # Reverse SQL (constraint will be dropped with model changes)
            reverse_sql="ALTER TABLE evaluation_evalform DROP CONSTRAINT IF EXISTS uq_evalform_one_active_per_dept_per_type;"
        ),
        
        # Create an index to improve performance of the constraint check
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_evalform_active_dept_name 
            ON evaluation_evalform (department_id, name) 
            WHERE is_active = true;
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_evalform_active_dept_name;"
        ),
    ]
