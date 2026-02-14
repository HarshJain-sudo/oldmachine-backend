# APIs to test (Seller Portal)

All **Seller Portal** endpoints require **seller authentication**: use a user that is linked to a **Seller** (via SellerProfile) and send the token in the header: `Authorization: Bearer <access_token>`.

Base URL (local): **`http://127.0.0.1:8000/api/seller-portal/`**

---

## 1. GET root categories

**Purpose:** First step in the flow. Returns top-level categories (no parent).

| Item   | Value |
|--------|--------|
| **URL** | `GET /api/seller-portal/categories/roots/` |
| **Auth** | Required (seller) |
| **Body** | None |

**Example:**
```http
GET http://127.0.0.1:8000/api/seller-portal/categories/roots/
Authorization: Bearer <seller_access_token>
```

**Response (200):** `{ "categories": [ { "category_code", "category_name", "level", "has_children", "is_leaf", "description", "image_url", ... } ] }`

---

## 2. GET children of a category

**Purpose:** After selecting a category, get its direct sub-categories. Call until the chosen category has `is_leaf: true`.

| Item   | Value |
|--------|--------|
| **URL** | `GET /api/seller-portal/categories/children/<category_code>/` |
| **Auth** | Required (seller) |
| **Body** | None |

**Example:**
```http
GET http://127.0.0.1:8000/api/seller-portal/categories/children/CNC_AND_LATHE_MACHINE/
Authorization: Bearer <seller_access_token>
```

**Response (200):** Same shape as roots: `{ "categories": [ ... ] }`

---

## 3. GET form config for a leaf category

**Purpose:** For the final (leaf) category, get the form schema. Frontend uses `schema` to render the form; submitted values are sent as `extra_info` in POST create product.

| Item   | Value |
|--------|--------|
| **URL** | `GET /api/seller-portal/form/<category_code>/` |
| **Auth** | Required (seller) |
| **Body** | None |

**Example:**
```http
GET http://127.0.0.1:8000/api/seller-portal/form/LATHE_MACHINE/
Authorization: Bearer <seller_access_token>
```

**Response (200):** `{ "category_code", "category_name", "schema": [ { "field_name", "field_label", "field_type", "is_required", "order", "options", "placeholder", ... } ], "is_leaf": true }`

Use `field_name` values as keys in `extra_info` when creating the product.

---

## 4. POST create product

**Purpose:** Create a product under a **leaf** category. Include form answers in `extra_info` (keys = `field_name` from the form schema).

| Item   | Value |
|--------|--------|
| **URL** | `POST /api/seller-portal/products/` |
| **Auth** | Required (seller) |
| **Body** | JSON (see below) |

**Request body:**
```json
{
  "category_code": "LATHE_MACHINE",
  "name": "Manual Lathe 2020",
  "description": "Optional description",
  "price": 150000,
  "currency": "INR",
  "tag": "Used",
  "availability": "In Stock",
  "extra_info": {
    "machine_type": "Manual Lathe",
    "brand_name": "HMT",
    "manufacturing_year": "2020-01-01",
    "machine_condition": "Good",
    "bed_length": "6",
    "working_status": "Running",
    "asking_price": "150000",
    "price_type": "Negotiable",
    "machine_location": "Pune, Maharashtra",
    "machine_description": "Well maintained",
    "machine_images": ["<file_id_or_url_if_you_store_files>"],
    "invoice_bill": null
  }
}
```

**Required:** `category_code`, `name`.  
**Optional:** `description`, `price`, `currency`, `tag`, `availability`, `extra_info`, `location`.  
If the category has a form config, every **required** field in `schema` must be present in `extra_info`.

**Example:**
```http
POST http://127.0.0.1:8000/api/seller-portal/products/
Authorization: Bearer <seller_access_token>
Content-Type: application/json

{ "category_code": "LATHE_MACHINE", "name": "My Lathe", "extra_info": { ... } }
```

**Response (201):** Created seller product with `id`, `product`, `product_details`, `seller`, `status`, `extra_info`, etc.

---

## Quick test order

1. **GET** `/api/seller-portal/categories/roots/` → pick a `category_code`.
2. **GET** `/api/seller-portal/categories/children/<that_code>/` → repeat until you get a category with `is_leaf: true`.
3. **GET** `/api/seller-portal/form/<leaf_code>/` → note `schema[].field_name` and required fields.
4. **POST** `/api/seller-portal/products/` with `category_code` = that leaf, `name`, and `extra_info` with keys from the schema.

---

## Swagger

Interactive docs: **http://127.0.0.1:8000/swagger/**  
Seller Portal endpoints are under the **Seller Portal** tag. You can authorize with a Bearer token there.
