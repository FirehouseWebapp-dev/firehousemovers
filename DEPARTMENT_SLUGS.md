# Department Slug Reference

## Overview
Department slugs are used to:
1. Generate URLs for department dashboards (e.g., `/dashboard/drivers/`)
2. Determine which evaluation questions to automatically create for each department

## Required Slug Values

When creating or editing departments, use these **exact slug values** to get the correct evaluation questions:

| Slug | Department Name | Evaluation Questions |
|------|----------------|---------------------|
| `sales` | Sales | Lead inquiries, conversion rates, sales records accuracy, customer satisfaction, sales goals |
| `accounting` | Accounting | Financial tasks completed, error-free percentage, documentation accuracy, timeliness, compliance |
| `claims` | Claims | Claims processed, resolution timeframe, documentation & communication, customer satisfaction, complex claims |
| `it` | IT | Support tickets completed, SLA compliance, troubleshooting effectiveness, user satisfaction, system reliability |
| `operations` | Operations | Operations handled, damage-free percentage, team leadership, customer satisfaction, workload management |
| `warehouse` | Warehouse | Tasks completed, damage prevention, inventory accuracy, loading efficiency, safety & organization |
| `drivers` | Drivers | Deliveries completed, on-time & incident-free, safety compliance, professionalism, priority moves |

## Current Departments

| Title | Slug | Status |
|-------|------|--------|
| SALES | `sales` | ✓ Configured |
| Accounting | `accounting` | ✓ Configured |
| Claims | `claims` | ✓ Configured |
| IT | `it` | ✓ Configured |
| Operations | `operations` | ✓ Configured |
| Warehouse | `warehouse` | ✓ Configured |
| Drivers department | `drivers` | ✓ Configured |

## Important Notes

1. **Slug values are case-sensitive** - use lowercase only
2. **Slugs must be unique** - no two departments can have the same slug
3. **Slugs are used in URLs** - keep them simple and URL-friendly
4. **Custom slugs are allowed** but won't have predefined evaluation questions
5. **Evaluation questions are defined in** `evaluation/signals.py` in the `DEFAULT_QUESTIONS` dictionary

## Creating New Departments

When creating a new department:

1. Choose a descriptive **Title** (e.g., "Drivers Department", "SALES")
2. Select the appropriate **Slug** from the list above (e.g., "drivers", "sales")
3. The slug determines which evaluation questions will be automatically created
4. If you use a custom slug not in the list, you'll need to manually create evaluation questions

## Technical Details

- **File**: `authentication/models.py` - Department model
- **File**: `authentication/forms.py` - Department form with slug field
- **File**: `evaluation/signals.py` - Question generation based on slugs (lines 11-86)
- **Admin**: Django admin shows slug field when creating/editing departments

