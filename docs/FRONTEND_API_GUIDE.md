# Frontend API Guide — OldMachine Backend

This document describes **API flows and endpoints** for the frontend: when to call which API, in what order, and what to send/expect. Use it together with **Swagger** (`/swagger/` or `/api-docs/`) and **ReDoc** (`/redoc/`) for full request/response schemas.

**Base URL:** `{BASE_URL}/api` (e.g. `https://api.example.com/api`)

- **Marketplace (buyer + auth):** `{BASE_URL}/api/marketplace/`
- **Seller portal:** `{BASE_URL}/api/seller-portal/`

---

## 1. Response and error format

- **Success:** Response body is the payload directly (no top-level `data` key unless stated).
- **Error:** JSON body:
  ```json
  {
    "response": "Human-readable message",
    "http_status_code": 400,
    "res_status": "MACHINE_READABLE_CODE"
  }
  ```
  Use `res_status` for branching (e.g. `INVALID_OTP`, `PRODUCT_NOT_FOUND`).

---

## 2. Authentication (marketplace)

All auth endpoints are under **`/api/marketplace/`** and do **not** require a token.

### 2.1 Login / sign-up flow (phone OTP)

| Step | Use case | Method | Endpoint | Body | Response |
|------|----------|--------|----------|------|----------|
| 1 | Send OTP to phone | POST | `/api/marketplace/login_or_sign_up/v1/` | `{ "phone_number": "9876543210", "country_code": "+91" }` | `{ "user_id": "uuid" }` |
| 2 | Verify OTP and get tokens | POST | `/api/marketplace/verify_otp/v1/` | `{ "phone_number": "9876543210", "otp": "123456" }` | `{ "access_token", "refresh_token", "token_type": "Bearer", "expires_in" }` |

- After step 2, store `access_token` and `refresh_token`.
- Send **Authorization:** `Bearer {access_token}` on all authenticated requests.

### 2.2 Refresh access token

| Use case | Method | Endpoint | Body | Response |
|----------|--------|----------|------|----------|
| Get new access token when expired | POST | `/api/marketplace/refresh_token/v1/` | `{ "refresh_token": "..." }` | `{ "access_token", "refresh_token", "token_type", "expires_in" }` |

Call this when the API returns **401**; then retry the original request with the new `access_token`.

---

## 3. Buyer flows (marketplace)

Buyer APIs are under **`/api/marketplace/`**. Most catalog endpoints accept **optional** auth: if you send a valid `Authorization: Bearer {access_token}`, the user gets recommendations and category-view tracking; if you don’t, they get public data only. **Invalid** token returns **401**.

### 3.1 Browse categories (home / category tree)

| Use case | Method | Endpoint | Auth | Query params | Response |
|----------|--------|----------|------|--------------|----------|
| Get categories with optional recommendations | GET | `/api/marketplace/categories_details/get/v1/` | Optional | `limit` (1–100, default 10), `offset` (default 0) | `{ "categories_details": [ { "id", "name", "category_code", "description", "level", "parent_category", "parent_category_name", "order", "image_url" } ], "recommended_products": [ { "category_name", "category_code", "category_image_url", "products": [ ... ] } ] }` |

- **recommended_products** is non-empty only when the user is authenticated.

### 3.2 Products in a category (simple list)

| Use case | Method | Endpoint | Auth | Query params | Response |
|----------|--------|----------|------|--------------|----------|
| Get products for a category | GET | `/api/marketplace/category_products_details/get/v1/` | Optional | **category_code** (required), `limit` (1–100), `offset` | `{ "products_details": [ { "name", "product_code", "seller_details", "tag", "image_urls", "location_details", "product_specifications", "price", "currency" } ], "total_count": "50" }` |

- If auth is sent, viewing this category is tracked for recommendations.

### 3.3 Search and filter products (advanced listing)

| Use case | Method | Endpoint | Auth | Body (JSON) | Response |
|----------|--------|----------|------|-------------|----------|
| Search/filter products with pagination | POST | `/api/marketplace/product_listings/search/v1/` | Optional | See below | `{ "products_details": [ ... ], "total_count": "42", "breadcrumbs": [ { "name", "category_code" } ] }` |

**Request body (all optional except pagination defaults):**

- **category_code** (string) — filter by category
- **min_price**, **max_price** (number)
- **condition** (string) — e.g. "Excellent", "Good"
- **state**, **district** (string) — location
- **location_search** (string) — text search on state/district
- **year_from**, **year_to** (integer)
- **search** (string) — text search on name/description
- **sort** — `"newest_first"` \| `"price_asc"` \| `"price_desc"` (default `newest_first`)
- **limit** (1–100, default 10), **offset** (default 0)

**breadcrumbs** is present when **category_code** was sent (category path for UI).

### 3.4 Product detail page

| Use case | Method | Endpoint | Auth | Response |
|----------|--------|----------|------|----------|
| Get single product by code | GET | `/api/marketplace/product_details/get/v1/{product_code}/` | Optional | Product object: `name`, `product_code`, `description`, `seller_details`, `tag`, `image_urls`, `location_details`, `product_specifications`, `price`, `currency`, `availability`, etc. |

- If auth is sent, viewing this product’s category is tracked for recommendations.

### 3.5 Saved searches (authenticated buyer only)

| Use case | Method | Endpoint | Auth | Request | Response |
|----------|--------|----------|------|---------|----------|
| List saved searches | GET | `/api/marketplace/saved_searches/` | Required | — | `{ "saved_searches": [ { "id", "name", "category_code", "query_params", "created_at" } ] }` |
| Create saved search | POST | `/api/marketplace/saved_searches/` | Required | `{ "name" (optional), "category_code" (optional), "query_params" (object, optional) }` | Created saved search object (201) |
| Delete saved search | DELETE | `/api/marketplace/saved_searches/{saved_search_id}/` | Required | — | 204 No Content |

- **query_params** should match the body you use for **product_listings/search** (filters, sort, etc.) so the frontend can restore the same search.

---

## 4. Seller flows (seller portal)

Seller APIs are under **`/api/seller-portal/`**. **All require authentication** and the user must have a **seller profile** (IsSeller). Use the same **Bearer** token obtained from marketplace auth (verify_otp).

### 4.1 Category tree for listing a product

Seller must pick a **leaf category** before creating a product. Flow:

| Step | Use case | Method | Endpoint | Auth | Response |
|------|----------|--------|----------|------|----------|
| 1 | Get root categories | GET | `/api/seller-portal/categories/roots/` | Required | `{ "categories": [ { "category_code", "category_name", "description", "image_url", "level", "parent_category_code", "parent_category_name", "full_path", "has_children", "is_leaf" } ] }` |
| 2 | Get children of a category | GET | `/api/seller-portal/categories/children/{category_code}/` | Required | Same shape: `{ "categories": [ ... ] }` |
| 3 | Repeat step 2 until **is_leaf** is true for the chosen category. | — | — | — | — |

- Only **leaf** categories (is_leaf === true) can have products. Use **category_code** from the chosen leaf in the create-product payload.

### 4.2 Get form config for a leaf category

| Use case | Method | Endpoint | Auth | Response |
|----------|--------|----------|------|----------|
| Get dynamic form schema for a leaf category | GET | `/api/seller-portal/form/{category_code}/` | Required | `{ "id", "category", "category_code", "category_name", "is_active", "schema": [ { "field_name", "field_label", "field_type", "is_required", "order", "options", "placeholder", ... } ], "is_leaf": true }` |

- **schema** is an array of field definitions. Render form controls by **field_type** (text, number, textarea, select, date, file, etc.). On submit, send values keyed by **field_name** inside **extra_info** (see create product).

### 4.3 Create product (seller)

| Use case | Method | Endpoint | Auth | Body | Response |
|----------|--------|----------|------|------|----------|
| Create a new product | POST | `/api/seller-portal/products/` | Required | See below | 201 + seller product object |

**Request body (JSON + optional multipart for images):**

- **category_code** (string, required) — must be a **leaf** category.
- **name** (string, required)
- **description** (string, optional)
- **price** (number, optional), **currency** (string, default "INR")
- **tag** (string, optional), **availability** (string, default "In Stock")
- **extra_info** (object, optional) — key-value from the form; keys = **field_name** from form config.
- **location** (object, optional) — e.g. `{ "state": "...", "district": "..." }`
- **images** (optional) — multipart file list (e.g. `images[]`)

### 4.4 List / update / de-list seller products

| Use case | Method | Endpoint | Auth | Query / Body | Response |
|----------|--------|----------|------|--------------|----------|
| List my products | GET | `/api/seller-portal/products/` | Required | Query: `status` (optional), `limit`, `offset` | `{ "products": [ ... ], "total_count": "10" }` |
| Get one product | GET | `/api/seller-portal/products/{seller_product_id}/` | Required | — | Single seller product object |
| Update product | PUT or PATCH | `/api/seller-portal/products/{seller_product_id}/` | Required | Same shape as create (partial for PATCH) | Updated object |
| De-list (soft) | DELETE | `/api/seller-portal/products/{seller_product_id}/` | Required | — | 204 No Content |

- **status** filter: `draft`, `pending_approval`, `approved`, `rejected`, `listed`.

---

## 5. Typical flows summary

| User type | Flow | APIs to call (in order) |
|-----------|------|---------------------------|
| **Buyer (anonymous)** | Browse and search | 1) GET categories_details 2) GET category_products_details or POST product_listings/search 3) GET product_details/{product_code} |
| **Buyer (login)** | Login then browse | 1) POST login_or_sign_up 2) POST verify_otp (store tokens) 3) Same as above with **Authorization: Bearer {access_token}** for recommendations and saved searches |
| **Buyer (saved search)** | Save / restore search | 1) POST saved_searches (body = name + query_params from current filters) 2) Later: GET saved_searches; use query_params as body for POST product_listings/search |
| **Seller** | List a product | 1) POST login_or_sign_up → verify_otp (if not logged in) 2) GET categories/roots/ 3) GET categories/children/{code}/ until leaf 4) GET form/{category_code}/ 5) POST products/ with category_code, name, extra_info from form, optional images |
| **Seller** | Manage my products | 1) GET seller-portal/products/ (optional ?status=) 2) GET/PUT/PATCH/DELETE products/{id}/ as needed |
| **Any** | Token expired | 1) POST refresh_token with refresh_token 2) Retry failed request with new access_token |

---

## 6. OpenAPI / Swagger

- **Swagger UI:** `{BASE_URL}/swagger/` or `{BASE_URL}/api-docs/`
- **ReDoc:** `{BASE_URL}/redoc/`
- **Schema JSON:** `{BASE_URL}/swagger.json`

Use these for exact request/response schemas, query parameters, and examples. This guide is for flow and use-case context; Swagger remains the source of truth for payload shapes.
