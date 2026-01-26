# Seller Product Listing Feature - Implementation Plan

## Overview
This feature allows sellers to list products through a dynamic form system where each category has its own configurable form fields. Products can be created, updated, and managed by sellers, with a future approval workflow.

## Understanding

### Current State
- `Seller` model exists (simple: id, name)
- `Product` model exists with seller relationship
- Products have images, specifications, location, etc.
- No seller portal or product creation flow for sellers

### Requirements
1. **Category-Based Form Configuration**
   - Each category has its own form configuration
   - Business can configure which fields to show
   - Fields can be required or optional
   - Different field types (text, number, select, file, etc.)

2. **Seller Product Management**
   - Sellers select a category
   - Form renders based on category configuration
   - Sellers fill form and upload images
   - Products are created and listed

3. **Future Approval Workflow**
   - Products will need approval before listing
   - Status: Draft → Pending Approval → Approved → Listed
   - Currently: Direct listing (no approval)

## Architecture Decision

### New App: `olmachine_seller_portal`
This app will handle:
- Form configuration management
- Seller product creation/management
- Approval workflow (future)

**Why separate app?**
- Clean separation of concerns
- Seller portal is distinct from marketplace browsing
- Easier to maintain and extend

## Database Models

### 1. CategoryFormConfig
Stores form configuration for each category.

```python
- id (UUID)
- category (ForeignKey to Category) - One config per category
- is_active (Boolean) - Enable/disable form
- created_at, updated_at
```

### 2. FormField
Individual field configuration within a form.

```python
- id (UUID)
- form_config (ForeignKey to CategoryFormConfig)
- field_name (CharField) - Internal field name (e.g., "brand", "model")
- field_label (CharField) - Display label (e.g., "Brand Name")
- field_type (CharField) - text, number, textarea, select, checkbox, radio, file, date, email, url
- is_required (Boolean)
- placeholder (CharField, optional)
- help_text (TextField, optional)
- default_value (CharField, optional)
- validation_rules (JSONField) - min/max length, regex, etc.
- options (JSONField) - For select/radio fields: [{"value": "option1", "label": "Option 1"}]
- order (IntegerField) - Display order
- created_at, updated_at
```

### 3. SellerProfile (Extend Seller)
Link sellers to users and add seller-specific data.

```python
- seller (OneToOne to Seller)
- user (ForeignKey to User) - Link seller to authenticated user
- business_name (CharField)
- business_address (TextField)
- phone_number (CharField)
- email (EmailField)
- is_verified (Boolean)
- created_at, updated_at
```

### 4. SellerProduct (Extend Product)
Products created by sellers with approval status.

```python
- product (OneToOne to Product) - Link to existing Product model
- seller (ForeignKey to Seller)
- status (CharField) - draft, pending_approval, approved, rejected, listed
- rejection_reason (TextField, optional)
- approved_by (ForeignKey to User, optional)
- approved_at (DateTimeField, optional)
- form_data (JSONField) - Store all form field values
- created_at, updated_at
```

### 5. ProductApproval (Future)
Track approval history and comments.

```python
- id (UUID)
- seller_product (ForeignKey to SellerProduct)
- status (CharField) - pending, approved, rejected
- reviewed_by (ForeignKey to User)
- comments (TextField, optional)
- created_at, updated_at
```

## API Endpoints

### Form Configuration APIs (Admin/Business)

1. **GET /api/seller-portal/category-form-configs/**
   - List all category form configurations
   - Query params: `category_code` (filter by category)
   - Response: List of form configs with fields

2. **GET /api/seller-portal/category-form-configs/{category_code}/**
   - Get form configuration for a specific category
   - Response: Form config with all fields in order

3. **POST /api/seller-portal/category-form-configs/**
   - Create form configuration for a category
   - Body: `category_code`, `is_active`, `fields[]`
   - Auth: Admin only

4. **PUT /api/seller-portal/category-form-configs/{id}/**
   - Update form configuration
   - Auth: Admin only

5. **DELETE /api/seller-portal/category-form-configs/{id}/**
   - Delete form configuration
   - Auth: Admin only

### Seller Product Management APIs

6. **GET /api/seller-portal/categories/with-forms/**
   - List categories that have form configurations
   - Response: Categories with form availability status
   - Auth: Seller (authenticated)

7. **GET /api/seller-portal/form/{category_code}/**
   - Get form configuration for seller to fill
   - Response: Form fields with labels, types, validation
   - Auth: Seller (authenticated)

8. **POST /api/seller-portal/products/**
   - Create a new product (seller submits form)
   - Body: 
     ```json
     {
       "category_code": "CAT001",
       "form_data": {
         "name": "Product Name",
         "brand": "Brand Name",
         "model": "Model Number",
         "price": "1000",
         "description": "Product description",
         ...
       },
       "images": [file1, file2, ...],
       "location": {
         "state": "State",
         "district": "District"
       }
     }
     ```
   - Response: Created product with status
   - Auth: Seller (authenticated)
   - Status: "draft" or "listed" (based on approval requirement)

9. **GET /api/seller-portal/products/**
   - List seller's products
   - Query params: `status` (filter by status), `category_code`, `limit`, `offset`
   - Response: List of seller's products
   - Auth: Seller (authenticated)

10. **GET /api/seller-portal/products/{product_id}/**
    - Get product details
    - Response: Product with form data
    - Auth: Seller (authenticated) - own products only

11. **PUT /api/seller-portal/products/{product_id}/**
    - Update product
    - Body: Same as create
    - Auth: Seller (authenticated) - own products only
    - Status: Can only update if status is "draft" or "rejected"

12. **DELETE /api/seller-portal/products/{product_id}/**
    - Delete product (soft delete or hard delete)
    - Auth: Seller (authenticated) - own products only

13. **POST /api/seller-portal/products/{product_id}/images/**
    - Add images to product
    - Body: `images[]` (files)
    - Auth: Seller (authenticated)

14. **DELETE /api/seller-portal/products/{product_id}/images/{image_id}/**
    - Delete product image
    - Auth: Seller (authenticated)

### Approval APIs (Future - Admin/Team)

15. **GET /api/seller-portal/products/pending-approval/**
    - List products pending approval
    - Query params: `category_code`, `seller_id`, `limit`, `offset`
    - Auth: Admin/Team

16. **POST /api/seller-portal/products/{product_id}/approve/**
    - Approve product
    - Body: `comments` (optional)
    - Auth: Admin/Team
    - Updates status to "approved" → "listed"

17. **POST /api/seller-portal/products/{product_id}/reject/**
    - Reject product
    - Body: `rejection_reason` (required)
    - Auth: Admin/Team
    - Updates status to "rejected"

## Field Types Supported

1. **text** - Single line text input
2. **number** - Numeric input (integer/decimal)
3. **textarea** - Multi-line text input
4. **select** - Dropdown selection
5. **radio** - Radio button selection
6. **checkbox** - Checkbox (boolean)
7. **file** - File upload (images)
8. **date** - Date picker
9. **email** - Email input with validation
10. **url** - URL input with validation

## Implementation Steps

### Phase 1: Core Models & Admin
1. Create `olmachine_seller_portal` app
2. Create models: `CategoryFormConfig`, `FormField`, `SellerProfile`, `SellerProduct`
3. Create migrations
4. Register models in admin
5. Create admin interfaces for form configuration

### Phase 2: Form Configuration APIs
1. Create serializers for form config and fields
2. Create views for form configuration CRUD
3. Add URL routing
4. Add Swagger documentation

### Phase 3: Seller Product APIs
1. Create serializers for seller products
2. Create views for product CRUD
3. Implement image upload handling
4. Add form validation based on configuration
5. Add URL routing
6. Add Swagger documentation

### Phase 4: Integration
1. Link sellers to users (SellerProfile)
2. Update existing Product model if needed
3. Test end-to-end flow
4. Add error handling

### Phase 5: Future - Approval Workflow
1. Add approval status management
2. Create approval APIs
3. Add notification system (optional)
4. Add approval dashboard

## File Structure

```
olmachine_seller_portal/
├── __init__.py
├── apps.py
├── admin.py
├── models.py
│   - CategoryFormConfig
│   - FormField
│   - SellerProfile
│   - SellerProduct
│   - ProductApproval (future)
├── serializers.py
│   - CategoryFormConfigSerializer
│   - FormFieldSerializer
│   - SellerProductSerializer
│   - ProductFormDataSerializer
├── views.py
│   - CategoryFormConfigViewSet
│   - SellerProductViewSet
│   - ProductApprovalViewSet (future)
├── services/
│   ├── __init__.py
│   ├── form_service.py
│   │   - Form validation
│   │   - Form data processing
│   └── product_service.py
│       - Product creation logic
│       - Image handling
├── permissions.py
│   - IsSeller
│   - IsAdminOrTeam
├── urls.py
└── migrations/
```

## Security & Permissions

1. **Seller Permissions**
   - Can only create/update/delete their own products
   - Can only view their own products
   - Must be authenticated

2. **Admin Permissions**
   - Can manage form configurations
   - Can approve/reject products
   - Can view all products

3. **Validation**
   - Form field validation based on configuration
   - Image upload validation (size, type, count)
   - Required field validation

## Future Enhancements

1. **Approval Workflow**
   - Multi-level approval
   - Approval comments
   - Notification system

2. **Form Builder UI**
   - Drag-and-drop form builder
   - Preview functionality

3. **Product Templates**
   - Save product as template
   - Quick product creation from template

4. **Bulk Operations**
   - Bulk product creation
   - Bulk status updates

5. **Analytics**
   - Seller dashboard
   - Product performance metrics

## Questions to Clarify

1. Should sellers be linked to existing User model or separate?
2. Should Product model be extended or create new SellerProduct?
3. Image storage: Cloud storage (S3) or local?
4. Maximum number of images per product?
5. Form field limit per category?
6. Should form configurations be versioned?

