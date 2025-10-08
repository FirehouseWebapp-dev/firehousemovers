# Department Slug Reference

## Overview
Department slugs are used to:
1. Generate URLs for department dashboards (e.g., `/dashboard/drivers/`)
2. Determine which evaluation questions to automatically create for each department

## Required Slug Values

When creating or editing departments, use these **exact slug values** to get the correct evaluation questions:

| Slug | Department Name | Evaluation Questions |
|------|----------------|---------------------|
| `sales` | Sales | Lead generation, conversion rates, customer satisfaction, sales targets, deal closing |
| `accounting` | Accounting | Invoice processing, error rates, accuracy, task completion, financial deadlines |
| `claims` | Claims | Claims processed, resolution timeframes, documentation, customer communication, fairness |
| `it` | IT | Support requests, SLA compliance, system uptime, employee satisfaction, security |
| `operations` | Operations | Moves supervised, damage-free percentage, teamwork, customer satisfaction, workload handling |
| `warehouse` | Warehouse | Storage tasks, damage prevention, inventory accuracy, loading efficiency, safety |
| `drivers` | Drivers | Moves/deliveries completed, on-time percentage, safety compliance, professionalism, complex moves |

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

