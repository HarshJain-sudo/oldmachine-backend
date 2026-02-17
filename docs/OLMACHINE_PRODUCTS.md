# olmachine_products

# Name
olmachine_products

# Responsibility
`olmachine_products` is the **marketplace catalog** app for the OldMachine backend. It serves category hierarchy, product listings, and product details to buyers (and to the seller portal for form configs and product creation).

**What it does:**
- Exposes hierarchical categories (root → children → leaf) and product listings by category
- Serves product detail by `product_code`
- Tracks authenticated users’ category views (last 3) and returns personalized “recommended products” by category
- Ensures optional auth: endpoints work without token; if `Authorization` is sent, token must be valid (401 otherwise)

**What it does NOT do:**
- Does not authenticate users (that’s `olmachine_users`)
- Does not manage seller identity or product creation flows (that’s `olmachine_seller_portal`); it owns the shared `Category`, `Product`, `Seller`, `Location`, and related models that the seller portal uses

# Big Picture: How This Works

## The Problem We're Solving
Buyers (and sometimes unauthenticated visitors) need to:
1. See the category tree (e.g. Electronics → Mobile Phones → Smartphones)
2. Browse products in a category (including parent categories: show products from all descendant leaf categories)
3. Open a product and see full details (specs, images, seller, location, price)
4. Optionally get personalized recommendations based on recently viewed categories (only when logged in)

**Challenges:**
- Categories are hierarchical; products are attached to leaf categories; listing by a parent category must aggregate leaf products
- If the client sends a Bearer token, it must be valid (no “half-authenticated” state)
- Recommendations should be based on recent category views, with a small, fixed window (e.g. last 3 categories)

**Solution:**
`olmachine_products` provides three read-only APIs: categories list (with optional recommendations), category products (with optional view tracking), and product detail (with optional view tracking). It uses `AllowAnyOrValidToken`: no token → public access; token present → must be valid or 401.

## Architecture Overview

- **Categories:** Stored in a tree via `Category.parent_category` and `level`; `is_leaf_category()` determines if products are attached directly or via descendants.
- **Products:** Belong to one `Category`, one `Seller`, optionally one `Location`; have `ProductImage` and `ProductSpecification`; identified by `product_code`.
- **Recommendations:** `UserCategoryView` stores (user, category, viewed_at); `RecommendationService` keeps at most 3 most recent categories per user, then returns products from those categories (e.g. top 3 products per category).

# Key Entities

## Category
**What it is:** Hierarchical category (tree) for organizing products.

**Problem it solves:** Marketplace browse by category; seller portal uses same tree to choose category and load form config.

**Key fields:** `id`, `name`, `category_code` (unique), `description`, `parent_category` (FK to self, null for root), `level` (0 = root), `order`, `image_url`, `is_active`.

**Helpers:** `get_ancestors()`, `get_descendants()`, `get_all_descendant_ids()`, `is_leaf_category()`, `get_full_path()`.

---

## Seller
**What it is:** Seller entity; products reference it.

**Problem it solves:** Products are owned by a seller; seller portal links users to sellers via `SellerProfile` in `olmachine_seller_portal`.

---

## Location
**What it is:** State/district for product location.

**Key fields:** `state`, `district` (optional); unique together (state, district).

---

## Product
**What it is:** Marketplace product; belongs to one Category, one Seller, optional Location.

**Key fields:** `name`, `product_code` (unique), `description`, `category`, `seller`, `location`, `tag`, `price`, `currency`, `availability`, `is_active`.

---

## ProductImage
**What it is:** Image URL and display order for a product.

**Key fields:** `product` (FK), `image_url`, `order`.

---

## ProductSpecification
**What it is:** Key-value specs (e.g. "Brand": "X", "Condition": "Used").

**Key fields:** `product` (FK), `key`, `value`; unique together (product, key).

---

## UserCategoryView
**What it is:** Tracks which categories a user recently viewed (for recommendations).

**Problem it solves:** Personalized “recommended products” from last N categories (N = 3).

**Key fields:** `user` (FK to AUTH_USER_MODEL), `category` (FK), `viewed_at`, `updated_at`; unique together (user, category). Service keeps only last 3 categories per user.

# Complete User Journeys

## Flow 1: Browse Categories (Home / Category Tree)
**User story:** User opens marketplace and sees categories (and optionally recommendations).

**Steps:**
1. Client calls `GET /api/marketplace/categories_details/get/v1/?limit=10&offset=0` (optional `Authorization: Bearer <token>`).
2. If token is present and invalid → 401. If no token or valid token → proceed.
3. Active categories are fetched (filter `is_active=True`), ordered by level, order, name; paginated by limit/offset (limit 1–100, offset ≥ 0).
4. If user is authenticated, `RecommendationService.get_recommended_products(user, products_per_category=3)` runs: recent categories (up to 3) and top products per category.
5. Response: `categories_details` (list of category objects with id, name, category_code, level, parent_category, order, image_url, etc.) and `recommended_products` (list of { category_name, category_code, category_image_url, products }).
6. Unauthenticated users get empty `recommended_products`.

**Why this matters:** Single entry point for discovery; recommendations encourage engagement for logged-in users.

---

## Flow 2: List Products in a Category
**User story:** User selects a category and sees products (and optionally records view for recommendations).

**Steps:**
1. Client calls `GET /api/marketplace/category_products_details/get/v1/?category_code=MOB001&limit=10&offset=0` (optional Bearer token).
2. If token present and invalid → 401. If no token or valid token → proceed.
3. `category_code` required; if missing → 400 INVALID_CATEGORY_CODE. limit/offset validated (limit 1–100, offset ≥ 0).
4. Category is fetched by `category_code` and `is_active=True`; if not found → 400 INVALID_CATEGORY_CODE.
5. If user is authenticated, `RecommendationService.track_category_view(user, category)` is called: upsert `UserCategoryView`, keep only last 3 categories per user.
6. Products: if category is leaf, products are from that category; if parent, products are from all active descendant leaf categories (or the category itself if no leaves). Products filtered `is_active=True`, ordered by `-created_at`, paginated.
7. Response: `products_details` (list with name, product_code, seller_details, tag, image_urls, location_details, product_specifications) and `total_count`.

**Why this matters:** Correct aggregation for parent categories; view tracking powers recommendations without extra API.

---

## Flow 3: View Product Detail
**User story:** User opens a product page.

**Steps:**
1. Client calls `GET /api/marketplace/product_details/get/v1/<product_code>/` (optional Bearer token).
2. If token present and invalid → 401. Otherwise proceed.
3. Product is fetched by `product_code` and `is_active=True`; if not found → 404 PRODUCT_NOT_FOUND.
4. If user is authenticated, `RecommendationService.track_category_view(user, product.category)` records view of the product’s category.
5. Response: full product detail (name, product_code, description, seller_details, tag, image_urls, location_details, product_specifications, price, currency, availability, etc.).

**Why this matters:** Detail page is the main conversion point; tracking product’s category keeps recommendations relevant.

# Public HTTP APIs

All endpoints live under **`/api/marketplace/`**. Permission: **AllowAnyOrValidToken** (no token = public; invalid token = 401).

## Get Categories (with optional recommendations)
- **Endpoint:** `GET /api/marketplace/categories_details/get/v1/`
- **Query params:** `limit` (default 10, 1–100), `offset` (default 0, ≥ 0). Optional header: `Authorization: Bearer <access_token>`.
- **Success (200):** `{ "data": { "categories_details": [ ... ], "recommended_products": [ { "category_name", "category_code", "category_image_url", "products": [ { "name", "product_code", "image_url" } } } ] } }`
- **Errors:** 400 INVALID_LIMIT / INVALID_OFFSET; 401 if invalid token; 500 on server error.

---

## Get Category Products
- **Endpoint:** `GET /api/marketplace/category_products_details/get/v1/`
- **Query params:** `category_code` (required), `limit` (default 10, 1–100), `offset` (default 0). Optional: `Authorization: Bearer <access_token>`.
- **Success (200):** `{ "data": { "products_details": [ ... ], "total_count": "50" } }`
- **Errors:** 400 INVALID_CATEGORY_CODE (missing or unknown category), INVALID_LIMIT, INVALID_OFFSET; 401 if invalid token; 500 on server error.

---

## Get Product Details
- **Endpoint:** `GET /api/marketplace/product_details/get/v1/<product_code>/`
- **Path:** `product_code` (string). Optional: `Authorization: Bearer <access_token>`.
- **Success (200):** `{ "data": { "name", "product_code", "description", "seller_details", "tag", "image_urls", "location_details", "product_specifications", "price", "currency", "availability", ... } }`
- **Errors:** 404 PRODUCT_NOT_FOUND; 401 if invalid token; 500 on server error.

# Data Layer (Database Models)

- **categories:** id (UUID), name, category_code (unique), description, parent_category_id (FK, null), level, order, image_url, is_active, created_at, updated_at. Indexes on category_code, (parent_category, is_active, order), (level, is_active), (is_active, order).
- **sellers:** id (UUID), name, created_at, updated_at.
- **locations:** id (UUID), state, district; unique_together (state, district).
- **products:** id (UUID), name, product_code (unique), description, category_id, seller_id, location_id (nullable), tag, price, currency, availability, is_active, created_at, updated_at. Indexes on product_code, (category, is_active), seller.
- **product_images:** id (UUID), product_id, image_url, order, created_at. Index (product, order).
- **product_specifications:** id (UUID), product_id, key, value; unique_together (product, key). Index (product).
- **user_category_views:** id (UUID), user_id, category_id, viewed_at, updated_at; unique_together (user, category). Indexes (user, -viewed_at), (category). Ordering -viewed_at.

# Module Dependencies

## Internal
- **olmachine_users:** AUTH_USER_MODEL for `UserCategoryView.user`.
- **oldmachine_backend.utils.response_utils:** `success_response`, `error_response`.

## External
- **django**, **djangorestframework**, **drf-yasg** (Swagger).

# Important Business Rules

- **Leaf vs parent categories:** Products are attached only to categories that have no active children. Listing by parent category returns products from all descendant leaf categories (or the category itself if it has no leaves).
- **AllowAnyOrValidToken:** If `Authorization` header is present, authentication must succeed; otherwise 401. No token → anonymous access.
- **Recommendations:** At most 3 most recent categories per user; recommendations are top N products per those categories (e.g. 3 per category). Only when user is authenticated.
- **Pagination:** limit 1–100; offset ≥ 0. total_count returned for category products only.

# Summary

`olmachine_products` is the marketplace catalog: categories (hierarchical), category products (with leaf aggregation), and product detail. It supports optional auth and, when authenticated, tracks category views and returns personalized recommended products. Same Category/Product/Seller/Location models are used by `olmachine_seller_portal` for seller-side product creation.

**For new developers:** Start with the three GET endpoints and `AllowAnyOrValidToken`; then follow `RecommendationService.track_category_view` and `get_recommended_products` and the Category/Product models.
