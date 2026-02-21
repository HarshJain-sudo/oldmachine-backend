"""
Tests for product listings search API (POST) and related behaviour.

Run: python manage.py test olmachine_products.tests.test_product_listings_search
"""

import json
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from olmachine_products.models import (
    Category,
    Product,
    ProductSpecification,
    SavedSearch,
)
from olmachine_products.constants import (
    PRODUCT_SPEC_CONDITION_KEY,
    PRODUCT_SPEC_YEAR_KEY,
)

User = get_user_model()
SEARCH_URL = '/api/marketplace/product_listings/search/v1/'
SAVED_SEARCHES_URL = '/api/marketplace/saved_searches/'


class ProductListingsSearchValidationTests(TestCase):
    """Validation and error response cases."""

    def setUp(self):
        self.client = Client()

    def test_invalid_category_code_returns_400(self):
        response = self.client.post(
            SEARCH_URL,
            data=json.dumps({'category_code': 'INVALID_CODE'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('res_status', data)
        self.assertEqual(data.get('res_status'), 'INVALID_CATEGORY_CODE')

    def test_invalid_limit_returns_400(self):
        for limit in (0, 101, -1, 'x'):
            response = self.client.post(
                SEARCH_URL,
                data=json.dumps({'limit': limit}),
                content_type='application/json',
            )
            self.assertEqual(
                response.status_code, 400,
                f'limit={limit} should return 400'
            )
            self.assertEqual(response.json().get('res_status'), 'INVALID_LIMIT')

    def test_invalid_offset_returns_400(self):
        response = self.client.post(
            SEARCH_URL,
            data=json.dumps({'offset': -1}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('res_status'), 'INVALID_OFFSET')

    def test_invalid_sort_returns_400(self):
        response = self.client.post(
            SEARCH_URL,
            data=json.dumps({'sort': 'invalid_sort'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('res_status'), 'INVALID_SORT')

    def test_min_price_greater_than_max_price_returns_400(self):
        response = self.client.post(
            SEARCH_URL,
            data=json.dumps({
                'min_price': 10000,
                'max_price': 1000,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json().get('res_status'), 'INVALID_PRICE_RANGE'
        )

    def test_year_from_greater_than_year_to_returns_400(self):
        response = self.client.post(
            SEARCH_URL,
            data=json.dumps({
                'year_from': 2023,
                'year_to': 2020,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json().get('res_status'), 'INVALID_YEAR_RANGE'
        )

    def test_invalid_min_price_returns_400(self):
        response = self.client.post(
            SEARCH_URL,
            data=json.dumps({'min_price': 'not_a_number'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json().get('res_status'), 'INVALID_MIN_PRICE'
        )


class ProductListingsSearchFilterTests(TestCase):
    """Filter and response shape (requires sample data with condition/year)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cat = Category.objects.create(
            name='Test Cat',
            category_code='TCAT001',
            is_active=True,
        )
        cls.product_with_condition = Product.objects.create(
            name='Prod A',
            product_code='PRODA',
            category=cls.cat,
            seller=cls._get_or_create_seller(),
            price=Decimal('1000.00'),
            currency='INR',
            is_active=True,
        )
        ProductSpecification.objects.create(
            product=cls.product_with_condition,
            key=PRODUCT_SPEC_CONDITION_KEY,
            value='Excellent',
        )
        ProductSpecification.objects.create(
            product=cls.product_with_condition,
            key=PRODUCT_SPEC_YEAR_KEY,
            value='2022',
        )
        cls.product_other = Product.objects.create(
            name='Prod B',
            product_code='PRODB',
            category=cls.cat,
            seller=cls._get_or_create_seller(),
            price=Decimal('2000.00'),
            currency='INR',
            is_active=True,
        )
        ProductSpecification.objects.create(
            product=cls.product_other,
            key=PRODUCT_SPEC_CONDITION_KEY,
            value='Good',
        )
        ProductSpecification.objects.create(
            product=cls.product_other,
            key=PRODUCT_SPEC_YEAR_KEY,
            value='2020',
        )

    @classmethod
    def _get_or_create_seller(cls):
        from olmachine_products.models import Seller
        seller, _ = Seller.objects.get_or_create(
            name='Test Seller',
            defaults={},
        )
        return seller

    def setUp(self):
        self.client = Client()

    def test_response_has_products_details_and_total_count(self):
        response = self.client.post(
            SEARCH_URL,
            data=json.dumps({
                'category_code': 'TCAT001',
                'limit': 10,
                'offset': 0,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('products_details', data)
        self.assertIn('total_count', data)
        self.assertIsInstance(data['products_details'], list)
        self.assertIsInstance(data['total_count'], str)

    def test_response_includes_price_and_currency(self):
        response = self.client.post(
            SEARCH_URL,
            data=json.dumps({
                'category_code': 'TCAT001',
                'limit': 1,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        products = response.json().get('products_details', [])
        self.assertGreater(len(products), 0)
        self.assertIn('price', products[0])
        self.assertIn('currency', products[0])

    def test_condition_filter_returns_only_matching(self):
        response = self.client.post(
            SEARCH_URL,
            data=json.dumps({
                'category_code': 'TCAT001',
                'condition': 'Excellent',
                'limit': 10,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(int(data['total_count']), 1)
        self.assertEqual(
            data['products_details'][0]['product_code'],
            'PRODA'
        )

    def test_year_filter_returns_only_matching(self):
        response = self.client.post(
            SEARCH_URL,
            data=json.dumps({
                'category_code': 'TCAT001',
                'year_from': 2021,
                'year_to': 2023,
                'limit': 10,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(int(data['total_count']), 1)
        self.assertEqual(
            data['products_details'][0]['product_code'],
            'PRODA'
        )

    def test_breadcrumbs_when_category_code_present(self):
        response = self.client.post(
            SEARCH_URL,
            data=json.dumps({
                'category_code': 'TCAT001',
                'limit': 1,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('breadcrumbs', data)
        self.assertIsInstance(data['breadcrumbs'], list)
        self.assertGreater(len(data['breadcrumbs']), 0)
        self.assertIn('name', data['breadcrumbs'][0])
        self.assertIn('category_code', data['breadcrumbs'][0])

    def test_no_breadcrumbs_without_category_code(self):
        response = self.client.post(
            SEARCH_URL,
            data=json.dumps({'limit': 1, 'offset': 0}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertNotIn('breadcrumbs', data)

    def test_sort_price_asc(self):
        response = self.client.post(
            SEARCH_URL,
            data=json.dumps({
                'category_code': 'TCAT001',
                'sort': 'price_asc',
                'limit': 10,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        products = response.json().get('products_details', [])
        prices = [float(p['price']) for p in products if p.get('price')]
        self.assertEqual(prices, sorted(prices))

    def test_search_text_filters_by_name(self):
        response = self.client.post(
            SEARCH_URL,
            data=json.dumps({
                'category_code': 'TCAT001',
                'search': 'Prod A',
                'limit': 10,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(int(data['total_count']), 1)
        self.assertIn('Prod A', data['products_details'][0]['name'])

    def test_condition_with_no_match_returns_empty_list(self):
        response = self.client.post(
            SEARCH_URL,
            data=json.dumps({
                'category_code': 'TCAT001',
                'condition': 'Refurbished',
                'limit': 10,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(int(data['total_count']), 0)
        self.assertEqual(data['products_details'], [])


class SavedSearchAuthTests(TestCase):
    """Saved search requires authentication."""

    def setUp(self):
        self.client = Client()

    def test_list_saved_searches_without_auth_returns_401(self):
        response = self.client.get(SAVED_SEARCHES_URL)
        self.assertEqual(response.status_code, 401)

    def test_create_saved_search_without_auth_returns_401(self):
        response = self.client.post(
            SAVED_SEARCHES_URL,
            data=json.dumps({
                'name': 'My search',
                'category_code': 'ELEC001',
                'query_params': {},
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401)
