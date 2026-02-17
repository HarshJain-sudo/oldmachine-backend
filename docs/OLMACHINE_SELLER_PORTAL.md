# olmachine_seller_portal

# Name
olmachine_seller_portal

# Responsibility
`olmachine_seller_portal` is the **seller-facing app** for listing products on the OldMachine marketplace. It lets authenticated sellers choose a category (via a tree), load a category-specific form schema, and create a product by submitting form data plus core fields.

**What it does:**
- Exposes root categories and child categories (drill-down, max depth 5) for the seller portal only
- Provides form configuration (JSON schema) per leaf category so the frontend can render dynamic forms
- Creates products: one POST API that creates `Product`, `ProductSpecification`, `SellerProduct`, and optionally images; product is created in `olmachine_products` and linked via `SellerProduct` with status and `extra_info`
- Enforces seller identity: all endpoints require **IsAuthenticated** and **IsSeller** (user must have a `SellerProfile`)

**What it does NOT do:**
- Does not authenticate users (that’s `olmachine_users`)
- Does not define the shared category/product/seller/location models (that’s `olmachine_products`); it uses them and adds seller-portal-specific models (CategoryFormConfig, SellerProfile, SellerProduct, ProductApproval)
- Does not expose list/detail/update/delete for seller products in the current API set (only create)

# Big Picture: How This Works

## The Problem We're Solving
Sellers need to:
1. Navigate the same category tree as buyers (root → children → … → leaf)
2. At a leaf category, see a form whose fields are defined by the backend (e.g. Brand, Model, Condition for “Smartphones”)
3. Submit one request with core fields (name, description, price, etc.) plus form answers (extra_info) and optionally images and location
4. Have the system create the marketplace Product, specs, and a SellerProduct record (status e.g. listed) without the seller touching product_code or internal IDs

**Challenges:**
- Categories are hierarchical; products must be created only under leaf categories
- Form fields vary by category; backend defines schema, frontend renders; submission keys must match `field_name` in schema
- One API should create Product, ProductSpecification, SellerProduct, and optionally Location and ProductImage in a single transaction

**Solution:**
`olmachine_seller_portal` provides four APIs: roots → children → form config → create product. Category tree comes from `olmachine_products.Category`; form config from `CategoryFormConfig` (OneToOne leaf category); product creation is done by `ProductService.create_seller_product()`, which creates Product, ProductSpecification, SellerProduct, and optionally Location and ProductImage. All endpoints require a valid access token and a linked SellerProfile (IsSeller).

## Architecture Overview

- **Category tree:** Read-only from `olmachine_products.Category`. Roots = no parent; children = direct sub-categories; max depth 5 (MAX_CATEGORY_DEPTH). Leaf = no active children; only leaf categories have form config and can have products.
- **Form config:** `CategoryFormConfig` has a JSON `schema` (array of field definitions: field_name, field_label, field_type, is_required, order, options, etc.). Frontend uses this to build the form; submitted values go in `extra_info` (keys = field_name).
- **Product creation:** `ProductService.create_seller_product()` gets category by category_code (must be leaf), generates unique product_code, gets/creates Location from location_data, creates Product, creates ProductSpecification from extra_info key-value, creates SellerProduct (status 'listed', extra_info), then saves images (placeholder URL for now).

# Key Entities

## CategoryFormConfig
**What it is:** One-to-one configuration for a leaf category: JSON schema for the seller form.

**Problem it solves:** Different categories need different fields (e.g. smartphones vs furniture); product team configures once per leaf category; frontend renders form from schema.

**Key fields:** `category` (OneToOne to Category), `is_active`, `schema` (JSON array of { field_name, field_label, field_type, is_required, order, options, placeholder, help_text }).

**Used by:** Form config API (GET form/<category_code>/); create product serializer validates required schema fields are present in extra_info.

---

## SellerProfile
**What it is:** Links an authenticated user to a Seller (from olmachine_products).

**Problem it solves:** Seller portal APIs need to know “which seller is this user”; one user can have one seller profile; IsSeller permission checks existence of SellerProfile for request.user.

**Key fields:** `user` (FK to AUTH_USER_MODEL), `seller` (OneToOne to Seller), `business_name`, `business_address`, `phone_number`, `email`, `is_verified`.

---

## SellerProduct
**What it is:** Links a marketplace Product to a Seller with status and extra form data.

**Problem it solves:** Tracks seller-submitted products, status (draft, pending_approval, approved, rejected, listed), rejection reason, approval metadata; stores extra_info (form answers) and points to the shared Product.

**Key fields:** `product` (OneToOne to Product), `seller` (FK), `status`, `rejection_reason`, `approved_by`, `approved_at`, `extra_info` (JSON).

---

## ProductApproval
**What it is:** Approval history per SellerProduct (reviewed_by, comments, status).

**Problem it solves:** Audit trail and future multi-level approval; not yet used by the four public APIs.

---

## Category, Seller, Product, Location, ProductImage, ProductSpecification (olmachine_products)
**Used by:** Seller portal reads Category for tree and form config; ProductService creates Product, ProductSpecification, ProductImage, and uses Seller and Location. Seller is obtained from SellerProfile.seller.

# Complete User Journeys

## Flow 1: Seller Opens Portal and Sees Root Categories
**User story:** Seller is logged in and opens the “List a product” flow.

**Steps:**
1. Client sends `GET /api/seller-portal/categories/roots/` with `Authorization: Bearer <access_token>`.
2. If not authenticated → 401. If authenticated but no SellerProfile → 403 (IsSeller fails). If seller → proceed.
3. Root categories: `Category.objects.filter(is_active=True, parent_category__isnull=True).order_by('order', 'name')`.
4. Response: `{ "data": { "categories": [ { "category_code", "category_name", "description", "image_url", "level", "parent_category_code", "parent_category_name", "full_path", "has_children", "is_leaf" }, ... ] } }`.
5. Seller selects a category; if has_children is true, client calls children API next; if is_leaf, client calls form config API.

**Why this matters:** Single entry point for category selection; same tree as marketplace but seller-only API.

---

## Flow 2: Seller Drills Down to Leaf Category
**User story:** Seller selects “Electronics” then “Mobile Phones” then “Smartphones” (leaf).

**Steps:**
1. For each selected category with has_children, client calls `GET /api/seller-portal/categories/children/<category_code>/` with Bearer token.
2. Permission same as roots (IsAuthenticated, IsSeller).
3. Category is fetched by category_code and is_active; if not found → 404. If category.level >= MAX_CATEGORY_DEPTH - 1 (e.g. 4), return empty list (no deeper drill-down).
4. Children: `category.sub_categories.filter(is_active=True).order_by('order', 'name')`.
5. Response: same shape as roots, list of categories with has_children and is_leaf.
6. When seller selects a category with is_leaf=true, client stops drilling and calls form config for that category_code.

**Why this matters:** Bounded depth (5 levels); leaf is the only place where form config and product creation are allowed.

---

## Flow 3: Seller Loads Form for Leaf Category
**User story:** Seller has chosen leaf category “Smartphones”; UI needs form fields.

**Steps:**
1. Client sends `GET /api/seller-portal/form/<category_code>/` with Bearer token.
2. Permission: IsAuthenticated, IsSeller.
3. Category is fetched; if not found → 404. If not leaf (`not category.is_leaf_category()`) → 400 NOT_LEAF_CATEGORY (“Form is only available for leaf categories. Please select a sub-category.”).
4. CategoryFormConfig is fetched for that category and is_active=True; if not found → 404 FORM_CONFIG_NOT_FOUND.
5. Response: `{ "data": { "id", "category", "category_code", "category_name", "is_active", "schema": [ { "field_name", "field_label", "field_type", "is_required", "order", "options", "placeholder", "help_text" }, ... ], "is_leaf": true } }`.
6. Frontend builds form so that each input’s name/key equals field_name; on submit, values are sent as extra_info (key = field_name).

**Why this matters:** Dynamic forms per category; required fields in schema are enforced on create; field_name is the contract between form config and extra_info.

---

## Flow 4: Seller Submits Product (Create)
**User story:** Seller fills form and core fields, then submits.

**Steps:**
1. Client sends `POST /api/seller-portal/products/` with Bearer token and body: category_code, name, description (optional), price (optional), currency (optional), tag (optional), availability (optional), extra_info (object, keys = schema field_name), location (optional { state, district }), and optionally images (multipart).
2. Permission: IsAuthenticated, IsSeller. SellerProfile is fetched for request.user; if not found → 404 SELLER_PROFILE_NOT_FOUND.
3. SellerProductCreateSerializer validates: category_code exists and is leaf; extra_info is dict; if CategoryFormConfig exists for that category, every schema field with is_required must be present and non-empty in extra_info (validation error with field label if missing).
4. ProductService.create_seller_product(seller, category_code, name, ...): In a transaction: get category (leaf check again), generate unique product_code (e.g. CAT001-PROD-XXXXXX), get or create Location from location_data, create Product (name, product_code, description, category, seller, location, tag, price, currency, availability, is_active=True), create ProductSpecification for each extra_info key-value (non-empty), create SellerProduct (product, seller, status='listed', extra_info=extra_info), then save images (currently placeholder URL). Returns SellerProduct.
5. Response: 201 with SellerProductSerializer data (id, product, product_details, seller, seller_name, status, rejection_reason, approved_by, approved_by_name, approved_at, extra_info, created_at, updated_at). On ValueError (e.g. not leaf) → 400 VALIDATION_ERROR; on other errors → 500 ERROR.

**Why this matters:** Single API creates full product and listing; extra_info drives both ProductSpecification (for buyer-facing detail) and SellerProduct.extra_info (for seller/approval context). Product is immediately created and linked; status is set to 'listed' by the service.

# Public HTTP APIs

All endpoints live under **`/api/seller-portal/`**. All require **IsAuthenticated** and **IsSeller** (user must have a SellerProfile). Base URL pattern: project mounts seller portal at `api/seller-portal/`.

## Get Root Categories
- **Endpoint:** `GET /api/seller-portal/categories/roots/`
- **Auth:** Bearer token (required). User must be a seller.
- **Success (200):** `{ "data": { "categories": [ { "category_code", "category_name", "description", "image_url", "level", "parent_category_code", "parent_category_name", "full_path", "has_children", "is_leaf" }, ... ] } }`
- **Errors:** 401 Unauthorized; 403 if not a seller (no SellerProfile).

---

## Get Child Categories
- **Endpoint:** `GET /api/seller-portal/categories/children/<category_code>/`
- **Auth:** Bearer token (required). User must be a seller.
- **Success (200):** Same categories shape as roots. If category level is at max depth, returns empty list.
- **Errors:** 404 if category not found; 401/403 as above.

---

## Get Form Config (Leaf Category)
- **Endpoint:** `GET /api/seller-portal/form/<category_code>/`
- **Auth:** Bearer token (required). User must be a seller.
- **Success (200):** `{ "data": { "id", "category", "category_code", "category_name", "is_active", "schema": [ { "field_name", "field_label", "field_type", "is_required", "order", "options", "placeholder", "help_text" }, ... ], "is_leaf": true } }`
- **Errors:** 400 NOT_LEAF_CATEGORY (category has children); 404 FORM_CONFIG_NOT_FOUND or category not found; 401/403 as above.

---

## Create Product
- **Endpoint:** `POST /api/seller-portal/products/`
- **Auth:** Bearer token (required). User must be a seller.
- **Request body (JSON or multipart):** category_code (required), name (required), description (optional), price (optional), currency (optional, default INR), tag (optional), availability (optional, default 'In Stock'), extra_info (optional object; keys = schema field_name; required fields from form config must be present), location (optional { state, district }), images (optional list of files).
- **Success (201):** `{ "data": { "id", "product", "product_details", "seller", "seller_name", "status", "rejection_reason", "approved_by", "approved_by_name", "approved_at", "extra_info", "created_at", "updated_at" } }`
- **Errors:** 400 INVALID_DATA (serializer validation, e.g. missing required extra_info), VALIDATION_ERROR (e.g. not leaf); 404 SELLER_PROFILE_NOT_FOUND; 401/403; 500 ERROR.

# Service Layer

## ProductService (product_service.py)

**create_seller_product(seller, category_code, name, description='', price=None, currency='INR', tag=None, availability='In Stock', extra_info=None, images=None, location_data=None)**  
- Gets Category by category_code; enforces leaf.  
- Generates unique product_code (e.g. CAT001-PROD-XXXXXX).  
- Gets or creates Location from location_data.  
- Creates Product, then ProductSpecification from extra_info key-value, then SellerProduct (status='listed', extra_info).  
- Saves images via _save_product_images (currently placeholder URL).  
- All in one transaction. Returns SellerProduct; raises ValueError on validation (e.g. not leaf).

**_generate_product_code(category_code)**  
- Returns unique product_code; retries if collision.

**_save_product_images(product, images)**  
- Creates ProductImage rows; _upload_image is placeholder (returns example URL). Production should upload to S3/Cloudinary and store real URL.

# Data Layer (Database Models)

**olmachine_seller_portal models:**

- **category_form_configs:** id (UUID), category_id (OneToOne), is_active, schema (JSON), created_at, updated_at. Index (category, is_active).
- **seller_profiles:** id (UUID), seller_id (OneToOne), user_id (FK), business_name, business_address, phone_number, email, is_verified, created_at, updated_at. Indexes (user), (seller).
- **seller_products:** id (UUID), product_id (OneToOne), seller_id, status, rejection_reason, approved_by_id, approved_at, extra_info (JSON), created_at, updated_at. Indexes (seller, status), (status), (created_at).
- **product_approvals:** id (UUID), seller_product_id, status, reviewed_by_id, comments, created_at, updated_at. Index (seller_product, status).

**Shared (olmachine_products):** Category, Seller, Product, Location, ProductImage, ProductSpecification — see OLMACHINE_PRODUCTS.md.

# Configuration and Data Loading

- **MAX_CATEGORY_DEPTH = 5:** Root = 0; children API returns no deeper when level >= 4.
- **Form config:** Populated via admin or a data-loading command (e.g. load_category_data). Schema is JSON array; field_name must match keys sent in extra_info on create.
- **Product code format:** `{category_code}-PROD-{6-char alphanumeric}`; uniqueness enforced in ProductService.

# Module Dependencies

## Internal
- **olmachine_products:** Category, Seller, Product, Location, ProductImage, ProductSpecification. Category tree and product creation live there; seller portal reads category and writes product/specs/images/seller_product.
- **olmachine_users:** AUTH_USER_MODEL for SellerProfile.user and ProductApproval/SellerProduct approval fields.
- **oldmachine_backend.utils.response_utils:** success_response, error_response.

## External
- **django**, **djangorestframework**, **drf-yasg**.

# Important Business Rules

- **Leaf-only products:** Products can be created only under leaf categories. Serializer and ProductService both enforce this.
- **Form required fields:** If CategoryFormConfig exists for the category, every schema field with is_required must have a non-empty value in extra_info (key = field_name); otherwise 400 with message like “‘Field Label’ is required.”
- **IsSeller:** Every seller-portal API requires a SellerProfile for request.user; otherwise 403.
- **Product code:** Unique per product; generated server-side; format category_code-PROD-XXXXXX.
- **SellerProduct status:** Created with status 'listed' by ProductService (no draft/pending in current create flow).
- **Images:** Stored as ProductImage with URL; current implementation uses a placeholder URL; production should use cloud storage.

# Summary

`olmachine_seller_portal` provides the seller flow: roots → children → form config → create product. It uses the shared Category and Product models from `olmachine_products`, adds CategoryFormConfig (form schema per leaf), SellerProfile (user–seller link), and SellerProduct (listing + extra_info). All endpoints require authentication and IsSeller. Product creation is a single POST that creates Product, ProductSpecification, SellerProduct, and optionally Location and ProductImage in one transaction.

**For new developers:** Follow the four APIs in order; then trace ProductService.create_seller_product and the serializer validation (category_code + extra_info vs CategoryFormConfig.schema). Load category and form config data via admin or load_category_data command.
