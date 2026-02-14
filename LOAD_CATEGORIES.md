# Loading category and form config data

Use the management command to load categories and their form configs from a JSON file.

## JSON format

The file must be a **JSON array** of objects. Each object can have:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Display name |
| `category_code` | string | yes | Unique code (e.g. `LATHE_MACHINE`) |
| `parent_category_code` | string or null | - | Parent’s `category_code`; empty or null = root |
| `order` | number | - | Display order (default 0) |
| `description` | string | - | Optional description |
| `image_url` | string | - | Optional image URL |
| `is_active` | boolean or "TRUE"/"FALSE" | - | Default true |
| `category_fields_config` | array or JSON string | - | Form field definitions (see below) |

### `category_fields_config`

Either a JSON **array** of field objects, or a **string** containing that array. Each field object can have:

- `type`: `"SELECT"`, `"INPUT"`, `"DATE"`, `"FILE"`
- `field_id`: unique key (becomes `field_name` in schema)
- `label`: label (becomes `field_label`)
- `place_holder`, `default_value`, `relevant_condition`, `is_required`
- `validation_regexs`: array of `{ "regex", "message" }`
- `ui_type`: e.g. `"RADIO"`, `"COMBO_BOX"`
- `options`: array of `{ "label", "value", "condition" }`
- For INPUT: `is_number`, `is_text_area`, `suffix_value`, `prefix_value`
- For DATE: `min_date`, `max_date`, `is_future_date_allowed`
- For FILE: `max_file_size`, `is_pdf`

Invalid JSON in `category_fields_config` (e.g. missing values like `"is_number": ,`) will cause that category’s form config to be skipped; fix the source data and re-run.

## Commands

```bash
# Dry run (parse only, no DB writes)
python manage.py load_category_data /path/to/categories.json --dry-run

# Load into database
python manage.py load_category_data /path/to/categories.json
```

Categories are created in dependency order (roots first, then children). Existing categories with the same `category_code` are updated. Form configs are created or updated per category when `category_fields_config` is present and valid.

## Preparing your file

When building your JSON from a spreadsheet:

1. Export rows as JSON array of objects.
2. Ensure `category_code` is unique and `parent_category_code` matches a code in the same file (or is empty for roots).
3. For form configs, use valid JSON (no trailing commas, no missing values like `"is_number": ,`).
