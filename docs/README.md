# OldMachine Backend — App Documentation

This folder contains **module-level documentation** for the OldMachine Django apps. Each document follows a consistent format: responsibility, big picture, key entities, user flows, public APIs, data layer, dependencies, and summary.

## URL layout

- **`/api/marketplace/`** — Shared prefix for **buyer-facing** and **auth**:
  - **Auth (olmachine_users):** login/sign-up, verify OTP, refresh token
  - **Catalog (olmachine_products):** categories, category products, product detail
- **`/api/seller-portal/`** — **Seller-facing** only (categories tree, form config, create product)
- **`/admin/`** — Django admin  
- **`/o/`** — OAuth2 provider (used internally by olmachine_users for tokens)  
- **`/swagger/`, `/redoc/`, `/api-docs/`** — API docs (Swagger/ReDoc)

## App docs (all user flows)

| App | Doc | Purpose |
|-----|-----|--------|
| **olmachine_users** | [OLMACHINE_USERS.md](./OLMACHINE_USERS.md) | Auth: phone OTP, verify OTP, access/refresh tokens |
| **olmachine_products** | [OLMACHINE_PRODUCTS.md](./OLMACHINE_PRODUCTS.md) | Marketplace catalog: categories, category products, product detail, recommendations |
| **olmachine_seller_portal** | [OLMACHINE_SELLER_PORTAL.md](./OLMACHINE_SELLER_PORTAL.md) | Seller flow: root/child categories, form config, create product |

Each doc is descriptive and covers **all user flows** for that app.

## Frontend API guide

- **[FRONTEND_API_GUIDE.md](./FRONTEND_API_GUIDE.md)** — Flows and endpoints for the frontend: auth, buyer (categories, search, product detail, saved searches), seller (category tree, form config, create/list/update products). Use with Swagger/ReDoc for full schemas.

## Seeding

- **Categories:** To load the standard category dump run
  `python manage.py load_category_data` (uses
  `env_files/oldmachine_category_data_dump.json` by default).
