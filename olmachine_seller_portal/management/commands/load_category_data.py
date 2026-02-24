"""
Load category and form config data from a JSON file into Category and CategoryFormConfig.

Standard dump: env_files/oldmachine_category_data_dump.json. Load it with
  python manage.py load_category_data
  python manage.py load_category_data --dry-run
Or pass a path: python manage.py load_category_data /path/to/categories.json

Expected JSON: array of objects with:
  name, category_code, parent_category_code (null or "" for root),
  order, description, image_url, is_active ("TRUE"/"FALSE" or bool),
  category_fields_config (optional): JSON string or array of field definitions.
"""

import json
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from olmachine_products.models import Category
from olmachine_seller_portal.models import CategoryFormConfig

DEFAULT_CATEGORY_DUMP_PATH = os.path.join(
    settings.BASE_DIR,
    "env_files",
    "oldmachine_category_data_dump.json",
)


def _normalize_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return True
    return str(value).strip().upper() in ("TRUE", "1", "YES", "T", "Y")


def _map_field_type(item):
    """Map source type + flags to our field_type."""
    t = (item.get("type") or "").strip().upper()
    if t == "SELECT":
        return "select"
    if t == "DATE":
        return "date"
    if t == "FILE":
        return "file"
    if t == "INPUT":
        if item.get("is_number"):
            return "number"
        if item.get("is_text_area"):
            return "textarea"
        return "text"
    return "text"


def _source_config_to_schema(raw):
    """
    Convert category_fields_config (array of field defs) to our schema format.
    Preserves extra keys (validation_regexs, min_date, ui_type, etc.) for frontend.
    """
    if not raw:
        return []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return []
    if not isinstance(raw, list):
        return []
    schema = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        field_name = (item.get("field_id") or "").strip() or f"field_{i}"
        field_label = (item.get("label") or "").strip() or field_name
        field_type = _map_field_type(item)
        options = []
        for o in item.get("options") or []:
            if isinstance(o, dict):
                options.append({
                    "value": o.get("value", ""),
                    "label": o.get("label", ""),
                })
        entry = {
            "field_name": field_name,
            "field_label": field_label,
            "field_type": field_type,
            "is_required": _normalize_bool(item.get("is_required", False)),
            "order": i + 1,
            "placeholder": (item.get("place_holder") or "").strip(),
            "options": options,
        }
        # Preserve extra keys for frontend
        for key in (
            "validation_regexs", "min_date", "max_date", "suffix_value",
            "prefix_value", "ui_type", "relevant_condition", "default_value",
            "max_file_size", "is_pdf", "is_future_date_allowed"
        ):
            if key in item and item[key] is not None:
                entry[key] = item[key]
        schema.append(entry)
    return schema


def _compute_levels(rows):
    """Attach level to each row. Roots = 0, children = parent_level + 1."""
    code_to_index = {r.get("category_code"): i for i, r in enumerate(rows) if r.get("category_code")}
    levels = []
    for i, r in enumerate(rows):
        parent_code = (r.get("parent_category_code") or "").strip() or None
        if not parent_code:
            levels.append(0)
            continue
        if parent_code not in code_to_index:
            levels.append(0)
            continue
        parent_level = levels[code_to_index[parent_code]]
        levels.append(parent_level + 1)
    return levels


def _sort_for_create(rows):
    """Sort rows so parents are created before children (by level, then order)."""
    levels = _compute_levels(rows)
    for i, r in enumerate(rows):
        r["_level"] = levels[i]
    return sorted(rows, key=lambda x: (x["_level"], int(x.get("order") or 0), x.get("name") or ""))


class Command(BaseCommand):
    help = "Load categories and form configs from a JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path",
            type=str,
            nargs="?",
            default=None,
            help=(
                "Path to JSON file (array of category rows with category_fields_config). "
                "Defaults to env_files/oldmachine_category_data_dump.json if omitted."
            ),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate only; do not write to DB.",
        )

    def handle(self, *args, **options):
        path = options["file_path"] or DEFAULT_CATEGORY_DUMP_PATH
        dry_run = options["dry_run"]

        if not os.path.isfile(path):
            self.stderr.write(self.style.ERROR(f"File not found: {path}"))
            return

        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                self.stderr.write(self.style.ERROR(f"Invalid JSON: {e}"))
                return

        if not isinstance(data, list):
            self.stderr.write(self.style.ERROR("JSON root must be an array of category objects."))
            return

        # Normalize and filter
        rows = []
        for i, r in enumerate(data):
            if not isinstance(r, dict):
                self.stdout.write(self.style.WARNING(f"Row {i}: skip (not an object)."))
                continue
            code = (r.get("category_code") or "").strip()
            if not code:
                self.stdout.write(self.style.WARNING(f"Row {i}: skip (empty category_code)."))
                continue
            rows.append({
                "name": (r.get("name") or "").strip() or code,
                "category_code": code,
                "parent_category_code": (r.get("parent_category_code") or "").strip() or None,
                "order": int(r.get("order") or 0),
                "description": (r.get("description") or "").strip() or None,
                "image_url": (r.get("image_url") or "").strip() or None,
                "is_active": _normalize_bool(r.get("is_active", True)),
                "category_fields_config": r.get("category_fields_config"),
            })

        ordered = _sort_for_create(rows)
        self.stdout.write(self.style.SUCCESS(f"Parsed {len(ordered)} categories (dry_run={dry_run})."))

        if dry_run:
            for r in ordered:
                cfg = r.get("category_fields_config")
                schema_len = 0
                if cfg:
                    schema = _source_config_to_schema(cfg)
                    schema_len = len(schema)
                self.stdout.write(
                    f"  [{r['_level']}] {r['category_code']} -> {r['name']} (form fields: {schema_len})"
                )
            return

        created_cats = 0
        updated_cats = 0
        created_cfgs = 0
        updated_cfgs = 0
        parent_by_code = {}

        with transaction.atomic():
            for r in ordered:
                code = r["category_code"]
                parent_code = r.get("parent_category_code")
                parent = parent_by_code.get(parent_code) if parent_code else None

                cat, created = Category.objects.update_or_create(
                    category_code=code,
                    defaults={
                        "name": r["name"],
                        "parent_category": parent,
                        "order": r["order"],
                        "description": r["description"],
                        "image_url": r["image_url"],
                        "is_active": r["is_active"],
                    },
                )
                parent_by_code[code] = cat
                if created:
                    created_cats += 1
                else:
                    updated_cats += 1

                cfg_raw = r.get("category_fields_config")
                if cfg_raw is not None and (isinstance(cfg_raw, str) and cfg_raw.strip() or isinstance(cfg_raw, list)):
                    schema = _source_config_to_schema(cfg_raw)
                    _, cfg_created = CategoryFormConfig.objects.update_or_create(
                        category=cat,
                        defaults={"schema": schema, "is_active": True},
                    )
                    if cfg_created:
                        created_cfgs += 1
                    else:
                        updated_cfgs += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Categories: {created_cats} created, {updated_cats} updated. "
                f"Form configs: {created_cfgs} created, {updated_cfgs} updated."
            )
        )
