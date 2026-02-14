# Seller Portal – Implementation Summary

**API spec (request/response definitions):** `olmachine_seller_portal/api_spec.json` — Swagger 2.0 with definitions, parameters, responses, and paths for all 4 APIs. Use this for frontend integration.

---

## Seller flow (exact requirement)

1. **Seller sees root categories** – All categories that have no parent (top-level).
2. **Seller selects one parent** – Then selects one sub-category. If that category has children, they select again. This drill-down continues **up to 5 levels** (root = level 0).
3. **When the last selected category has no children (leaf)** – Return the **form config** for that category.
4. **Frontend** – Uses the form config (JSON schema) to render the form. Frontend may use JSON-stringified objects to control how the form is shown.
5. **Seller submits** – We store the filled data as **key-value** (e.g. `extra_info` and `ProductSpecification`).
6. **Buyer view** – When the product is listed, buyers see proper product details: we store key-value so the existing product detail API (which returns `product_specifications`) can show specs in an Indiamart-style listing.

---

## Category tree (max 5 levels)

- **Root categories**: categories with `parent_category = null`.
- **Children**: direct sub-categories of a given category. Depth is limited to 5 levels (level 0 = root … level 4).
- **Leaf**: a category with no active children. Only leaf categories can have a form config and list products.

---

## API endpoints (only these 4)

### 1. Root categories (seller entry point)

- **GET** `/api/seller-portal/categories/roots/`
- **Auth:** Seller (IsSeller).
- **Response:** List of root categories. Each item: `category_code`, `category_name`, `description`, `image_url`, `level`, `parent_category_code`, `parent_category_name`, `full_path`, `has_children`, `is_leaf`.

### 2. Child categories (drill-down)

- **GET** `/api/seller-portal/categories/children/<category_code>/`
- **Auth:** Seller.
- **Response:** Direct children of the given category. Same shape as above. Use until the user reaches a category with `has_children: false` (leaf). No children are returned when parent level is already at max depth.

### 3. Form config (for leaf category only)

- **GET** `/api/seller-portal/form/<category_code>/`
- **Auth:** Seller.
- **When:** Only for a **leaf** category (the one with no children after drill-down).
- **Response:** Form configuration for that category:
  - `category_code`, `category_name`, `id`, `is_active`, **`schema`**, `is_leaf`.
- **Schema:** JSON array of field definitions so the frontend can build the form. Example:
  ```json
  [
    { "field_name": "brand", "field_label": "Brand", "field_type": "text", "is_required": true, "order": 1 },
    { "field_name": "model", "field_label": "Model", "field_type": "text", "is_required": false, "order": 2 },
    { "field_name": "condition", "field_label": "Condition", "field_type": "select", "is_required": true, "order": 3, "options": [{"value": "new", "label": "New"}, {"value": "used", "label": "Used"}] }
  ]
  ```
- **Errors:** 400 if category is not leaf (“Select a sub-category”). 404 if category or form config not found.

### 4. Create product (after form is filled)

- **POST** `/api/seller-portal/products/`
- **Body:**  
  - `category_code` (required) – must be the **leaf** category for which the seller got the form.  
  - `name` (required).  
  - `description`, `price`, `currency`, `tag`, `availability` (optional).  
  - **`extra_info`** (required from form) – key-value object; keys match `field_name` in schema. Example: `{"brand": "X", "model": "Y", "condition": "used"}`.  
  - `location` (optional): `{ "state": "...", "district": "..." }`.  
  - `images[]` (optional) multipart.
- **Validation:** If the category has a form config, required fields from the schema must be present in `extra_info`.
- **Storage:**
  - **Seller side:** `SellerProduct.extra_info` stores the same key-value (for seller’s own view).
  - **Buyer side:** Each key-value in `extra_info` is stored as a **ProductSpecification** row (`key`, `value`). The existing product detail API returns `product_specifications` as a dict, so buyers see these as proper product details (Indiamart-style).

### 5. No other product APIs

- Only **POST /products/** exists. No list, get, update, or delete product endpoints in seller portal.

---

## Database models (seller portal)

- **CategoryFormConfig** – One per (leaf) category. Fields: `category` (OneToOne), `is_active`, **`schema`** (JSON array of field definitions). No separate FormField table; everything is in `schema`.
- **SellerProduct** – `extra_info` (JSON key-value) holds the form submission. Linked to `Product`; product has **ProductSpecification** rows created from `extra_info` for buyer display.

---

## How buyers see product details

- Product is stored in `olmachine_products.Product` with related **ProductSpecification** rows created from `extra_info` (key → `key`, value → `value`).
- Existing product APIs (e.g. product detail by id) return `product_specifications` as a dictionary. Frontend can render this like Indiamart (table or list of key-value rows). No extra API change needed for buyer side.

---

## Admin

- **Category Form Configuration** – Admin can add/edit form config per category: select category (leaf), set `is_active`, and edit **schema** (JSON array of field definitions). Same schema format as above.

---

## Summary

| # | API | Purpose |
|---|-----|--------|
| 1 | GET `/categories/roots/` | Show root categories (no parent). |
| 2 | GET `/categories/children/<code>/` | Drill down (max 5 levels). |
| 3 | GET `/form/<category_code>/` | When leaf selected, get form schema for frontend. |
| 4 | POST `/products/` with `extra_info` | Submit form as key-value; stored in `extra_info` and ProductSpecification for buyer. |

No other seller-portal APIs (no product list, detail, update, delete).

Form config is **one JSON field** per category (`schema`). Seller submission is **one key-value object** (`extra_info`). Buyer listing uses existing **product_specifications** built from that key-value.
