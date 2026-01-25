"""
Management command to populate sample data.

Usage:
    python manage.py populate_sample_data
"""

from django.core.management.base import BaseCommand
from olmachine_products.models import (
    Category,
    Seller,
    Location,
    Product,
    ProductImage,
    ProductSpecification
)


class Command(BaseCommand):
    """Command to populate sample data."""

    help = 'Populate database with sample categories, products, sellers, and locations'

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write(
            self.style.SUCCESS('Starting to populate sample data...')
        )

        # Create Categories
        categories_data = [
            {
                'name': 'Electronics',
                'category_code': 'ELEC001',
                'description': (
                    'Electronic products and accessories including '
                    'smartphones, laptops, tablets, and gadgets'
                ),
                'order': 1,
                'image_url': 'https://example.com/images/electronics.jpg'
            },
            {
                'name': 'Fashion',
                'category_code': 'FASH001',
                'description': (
                    'Clothing and fashion accessories for men, women, '
                    'and kids including apparel, shoes, and accessories'
                ),
                'order': 2,
                'image_url': 'https://example.com/images/fashion.jpg'
            },
            {
                'name': 'Home & Kitchen',
                'category_code': 'HOME001',
                'description': (
                    'Home appliances, kitchen items, furniture, '
                    'and home decor products'
                ),
                'order': 3,
                'image_url': 'https://example.com/images/home.jpg'
            },
            {
                'name': 'Sports & Fitness',
                'category_code': 'SPRT001',
                'description': (
                    'Sports equipment, fitness gear, gym accessories, '
                    'and outdoor sports items'
                ),
                'order': 4,
                'image_url': 'https://example.com/images/sports.jpg'
            },
            {
                'name': 'Books & Media',
                'category_code': 'BOOK001',
                'description': (
                    'Books, movies, music, educational materials, '
                    'and media products'
                ),
                'order': 5,
                'image_url': 'https://example.com/images/books.jpg'
            },
            {
                'name': 'Beauty & Personal Care',
                'category_code': 'BEAU001',
                'description': (
                    'Beauty products, skincare, haircare, '
                    'and personal care items'
                ),
                'order': 6,
                'image_url': 'https://example.com/images/beauty.jpg'
            },
            {
                'name': 'Automotive',
                'category_code': 'AUTO001',
                'description': (
                    'Car accessories, bike parts, automotive tools, '
                    'and vehicle maintenance products'
                ),
                'order': 7,
                'image_url': 'https://example.com/images/automotive.jpg'
            },
            {
                'name': 'Toys & Games',
                'category_code': 'TOYS001',
                'description': (
                    'Toys, games, puzzles, board games, '
                    'and children entertainment products'
                ),
                'order': 8,
                'image_url': 'https://example.com/images/toys.jpg'
            },
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                category_code=cat_data['category_code'],
                defaults=cat_data
            )
            categories[cat_data['category_code']] = category
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created category: {category.name}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Category already exists: {category.name}'
                    )
                )

        # Create Sellers
        sellers_data = [
            {'name': 'Tech Solutions Pvt Ltd'},
            {'name': 'Fashion Hub India'},
            {'name': 'Home Essentials Store'},
            {'name': 'Sports World'},
            {'name': 'Book Paradise'},
            {'name': 'ElectroMart'},
            {'name': 'Style Corner'},
        ]

        sellers = {}
        for seller_data in sellers_data:
            seller, created = Seller.objects.get_or_create(
                name=seller_data['name'],
                defaults=seller_data
            )
            sellers[seller_data['name']] = seller
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created seller: {seller.name}')
                )

        # Create Locations
        locations_data = [
            {'state': 'Maharashtra', 'district': 'Mumbai'},
            {'state': 'Delhi', 'district': 'New Delhi'},
            {'state': 'Karnataka', 'district': 'Bangalore'},
            {'state': 'Tamil Nadu', 'district': 'Chennai'},
            {'state': 'Gujarat', 'district': 'Ahmedabad'},
            {'state': 'West Bengal', 'district': 'Kolkata'},
        ]

        locations = {}
        for loc_data in locations_data:
            location, created = Location.objects.get_or_create(
                state=loc_data['state'],
                district=loc_data['district'],
                defaults=loc_data
            )
            locations[f"{loc_data['district']}, {loc_data['state']}"] = location
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created location: {location.district}, '
                        f'{location.state}'
                    )
                )

        # Create Products
        products_data = [
            {
                'name': 'Smartphone',
                'product_code': 'PROD001',
                'description': (
                    'Latest smartphone with advanced features, '
                    'high-resolution camera, and long battery life'
                ),
                'category': categories['ELEC001'],
                'seller': sellers['Tech Solutions Pvt Ltd'],
                'location': locations['Mumbai, Maharashtra'],
                'tag': 'Premium',
                'price': 25000.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/smartphone1.jpg',
                    'https://example.com/images/smartphone2.jpg',
                ],
                'specifications': {
                    'power': '5000mAh',
                    'country of origin': 'India',
                    'screen size': '6.5 inches',
                    'RAM': '8GB',
                    'storage': '128GB',
                }
            },
            {
                'name': 'Laptop',
                'product_code': 'PROD002',
                'description': (
                    'High-performance laptop for work and gaming, '
                    'with latest processor and graphics card'
                ),
                'category': categories['ELEC001'],
                'seller': sellers['ElectroMart'],
                'location': locations['Bangalore, Karnataka'],
                'tag': 'Best Seller',
                'price': 65000.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/laptop1.jpg',
                    'https://example.com/images/laptop2.jpg',
                ],
                'specifications': {
                    'processor': 'Intel Core i7',
                    'RAM': '16GB',
                    'storage': '512GB SSD',
                    'graphics': 'NVIDIA RTX 3050',
                    'country of origin': 'India',
                }
            },
            {
                'name': 'Wireless Headphones',
                'product_code': 'PROD003',
                'description': (
                    'Premium wireless headphones with noise cancellation '
                    'and long battery life'
                ),
                'category': categories['ELEC001'],
                'seller': sellers['Tech Solutions Pvt Ltd'],
                'location': locations['New Delhi, Delhi'],
                'tag': 'New',
                'price': 3500.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/headphones1.jpg',
                ],
                'specifications': {
                    'battery life': '30 hours',
                    'connectivity': 'Bluetooth 5.0',
                    'country of origin': 'China',
                }
            },
            {
                'name': 'Cotton T-Shirt',
                'product_code': 'PROD004',
                'description': (
                    'Comfortable cotton t-shirt, perfect for casual wear'
                ),
                'category': categories['FASH001'],
                'seller': sellers['Fashion Hub India'],
                'location': locations['Mumbai, Maharashtra'],
                'tag': 'Popular',
                'price': 599.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/tshirt1.jpg',
                    'https://example.com/images/tshirt2.jpg',
                ],
                'specifications': {
                    'material': '100% Cotton',
                    'sizes available': 'S, M, L, XL',
                    'country of origin': 'India',
                }
            },
            {
                'name': 'Running Shoes',
                'product_code': 'PROD005',
                'description': (
                    'Comfortable running shoes with cushioned sole '
                    'for long-distance running'
                ),
                'category': categories['SPRT001'],
                'seller': sellers['Sports World'],
                'location': locations['Chennai, Tamil Nadu'],
                'tag': 'Best Seller',
                'price': 2999.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/shoes1.jpg',
                    'https://example.com/images/shoes2.jpg',
                ],
                'specifications': {
                    'size': 'UK 7-11',
                    'material': 'Mesh and Synthetic',
                    'country of origin': 'India',
                }
            },
            {
                'name': 'Coffee Maker',
                'product_code': 'PROD006',
                'description': (
                    'Automatic coffee maker with programmable timer '
                    'and thermal carafe'
                ),
                'category': categories['HOME001'],
                'seller': sellers['Home Essentials Store'],
                'location': locations['Ahmedabad, Gujarat'],
                'tag': 'Premium',
                'price': 4500.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/coffeemaker1.jpg',
                ],
                'specifications': {
                    'capacity': '12 cups',
                    'power': '1000W',
                    'country of origin': 'India',
                }
            },
            {
                'name': 'Python Programming Book',
                'product_code': 'PROD007',
                'description': (
                    'Comprehensive guide to Python programming '
                    'for beginners and advanced users'
                ),
                'category': categories['BOOK001'],
                'seller': sellers['Book Paradise'],
                'location': locations['Kolkata, West Bengal'],
                'tag': 'Bestseller',
                'price': 899.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/book1.jpg',
                ],
                'specifications': {
                    'pages': '500',
                    'language': 'English',
                    'publisher': 'Tech Books',
                    'country of origin': 'India',
                }
            },
            {
                'name': 'Yoga Mat',
                'product_code': 'PROD008',
                'description': (
                    'Non-slip yoga mat with extra cushioning '
                    'for comfortable practice'
                ),
                'category': categories['SPRT001'],
                'seller': sellers['Sports World'],
                'location': locations['Bangalore, Karnataka'],
                'tag': 'Popular',
                'price': 1299.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/yogamat1.jpg',
                ],
                'specifications': {
                    'thickness': '6mm',
                    'material': 'TPE',
                    'size': '183cm x 61cm',
                    'country of origin': 'India',
                }
            },
            {
                'name': 'Designer Jeans',
                'product_code': 'PROD009',
                'description': (
                    'Premium designer jeans with perfect fit '
                    'and modern style'
                ),
                'category': categories['FASH001'],
                'seller': sellers['Style Corner'],
                'location': locations['Mumbai, Maharashtra'],
                'tag': 'Premium',
                'price': 2499.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/jeans1.jpg',
                    'https://example.com/images/jeans2.jpg',
                ],
                'specifications': {
                    'material': '98% Cotton, 2% Elastane',
                    'sizes available': '28, 30, 32, 34, 36',
                    'country of origin': 'India',
                }
            },
            {
                'name': 'Air Fryer',
                'product_code': 'PROD010',
                'description': (
                    'Digital air fryer with large capacity, '
                    'perfect for healthy cooking'
                ),
                'category': categories['HOME001'],
                'seller': sellers['Home Essentials Store'],
                'location': locations['New Delhi, Delhi'],
                'tag': 'New',
                'price': 5999.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/airfryer1.jpg',
                    'https://example.com/images/airfryer2.jpg',
                ],
                'specifications': {
                    'capacity': '5.5 Liters',
                    'power': '1500W',
                    'temperature range': '80°C - 200°C',
                    'country of origin': 'India',
                }
            },
            {
                'name': 'Tablet',
                'product_code': 'PROD011',
                'description': (
                    '10-inch Android tablet with high-resolution display, '
                    'perfect for work and entertainment'
                ),
                'category': categories['ELEC001'],
                'seller': sellers['ElectroMart'],
                'location': locations['Mumbai, Maharashtra'],
                'tag': 'Popular',
                'price': 15000.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/tablet1.jpg',
                    'https://example.com/images/tablet2.jpg',
                ],
                'specifications': {
                    'screen size': '10.1 inches',
                    'RAM': '4GB',
                    'storage': '64GB',
                    'battery': '7000mAh',
                    'country of origin': 'China',
                }
            },
            {
                'name': 'Smart Watch',
                'product_code': 'PROD012',
                'description': (
                    'Fitness smartwatch with heart rate monitor, '
                    'GPS, and 7-day battery life'
                ),
                'category': categories['ELEC001'],
                'seller': sellers['Tech Solutions Pvt Ltd'],
                'location': locations['Bangalore, Karnataka'],
                'tag': 'Best Seller',
                'price': 8999.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/smartwatch1.jpg',
                ],
                'specifications': {
                    'display': '1.4 inch AMOLED',
                    'battery life': '7 days',
                    'water resistance': '5 ATM',
                    'country of origin': 'China',
                }
            },
            {
                'name': 'Formal Shirt',
                'product_code': 'PROD013',
                'description': (
                    'Premium formal shirt with wrinkle-free fabric, '
                    'perfect for office wear'
                ),
                'category': categories['FASH001'],
                'seller': sellers['Style Corner'],
                'location': locations['New Delhi, Delhi'],
                'tag': 'Premium',
                'price': 1299.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/shirt1.jpg',
                    'https://example.com/images/shirt2.jpg',
                ],
                'specifications': {
                    'material': '100% Cotton',
                    'sizes available': 'S, M, L, XL, XXL',
                    'fit': 'Regular Fit',
                    'country of origin': 'India',
                }
            },
            {
                'name': 'Leather Jacket',
                'product_code': 'PROD014',
                'description': (
                    'Genuine leather jacket with quilted lining, '
                    'perfect for winter season'
                ),
                'category': categories['FASH001'],
                'seller': sellers['Fashion Hub India'],
                'location': locations['Mumbai, Maharashtra'],
                'tag': 'Premium',
                'price': 4999.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/jacket1.jpg',
                ],
                'specifications': {
                    'material': 'Genuine Leather',
                    'sizes available': 'M, L, XL, XXL',
                    'lining': 'Quilted',
                    'country of origin': 'India',
                }
            },
            {
                'name': 'Dumbbell Set',
                'product_code': 'PROD015',
                'description': (
                    'Adjustable dumbbell set with multiple weight options, '
                    'perfect for home gym'
                ),
                'category': categories['SPRT001'],
                'seller': sellers['Sports World'],
                'location': locations['Ahmedabad, Gujarat'],
                'tag': 'Popular',
                'price': 3499.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/dumbbell1.jpg',
                ],
                'specifications': {
                    'weight range': '5kg - 25kg per dumbbell',
                    'material': 'Cast Iron',
                    'country of origin': 'India',
                }
            },
            {
                'name': 'Basketball',
                'product_code': 'PROD016',
                'description': (
                    'Official size basketball with premium grip, '
                    'suitable for indoor and outdoor play'
                ),
                'category': categories['SPRT001'],
                'seller': sellers['Sports World'],
                'location': locations['Chennai, Tamil Nadu'],
                'tag': 'Popular',
                'price': 899.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/basketball1.jpg',
                ],
                'specifications': {
                    'size': 'Size 7 (Official)',
                    'material': 'Composite Leather',
                    'country of origin': 'China',
                }
            },
            {
                'name': 'Microwave Oven',
                'product_code': 'PROD017',
                'description': (
                    '20L capacity microwave oven with multiple cooking modes '
                    'and auto-defrost feature'
                ),
                'category': categories['HOME001'],
                'seller': sellers['Home Essentials Store'],
                'location': locations['Kolkata, West Bengal'],
                'tag': 'Best Seller',
                'price': 5499.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/microwave1.jpg',
                    'https://example.com/images/microwave2.jpg',
                ],
                'specifications': {
                    'capacity': '20 Liters',
                    'power': '800W',
                    'cooking modes': '5',
                    'country of origin': 'India',
                }
            },
            {
                'name': 'Vacuum Cleaner',
                'product_code': 'PROD018',
                'description': (
                    'Bagless vacuum cleaner with HEPA filter, '
                    'perfect for home cleaning'
                ),
                'category': categories['HOME001'],
                'seller': sellers['Home Essentials Store'],
                'location': locations['Bangalore, Karnataka'],
                'tag': 'New',
                'price': 6999.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/vacuum1.jpg',
                ],
                'specifications': {
                    'power': '2000W',
                    'capacity': '2 Liters',
                    'filter type': 'HEPA',
                    'country of origin': 'India',
                }
            },
            {
                'name': 'Django Web Development Book',
                'product_code': 'PROD019',
                'description': (
                    'Complete guide to Django web development '
                    'for building scalable web applications'
                ),
                'category': categories['BOOK001'],
                'seller': sellers['Book Paradise'],
                'location': locations['Mumbai, Maharashtra'],
                'tag': 'Bestseller',
                'price': 1299.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/djangobook1.jpg',
                ],
                'specifications': {
                    'pages': '650',
                    'language': 'English',
                    'publisher': 'Tech Publications',
                    'country of origin': 'India',
                }
            },
            {
                'name': 'Face Moisturizer',
                'product_code': 'PROD020',
                'description': (
                    'Hydrating face moisturizer with SPF 30, '
                    'suitable for all skin types'
                ),
                'category': categories.get('BEAU001'),
                'seller': sellers['Fashion Hub India'],
                'location': locations['New Delhi, Delhi'],
                'tag': 'Popular',
                'price': 799.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/moisturizer1.jpg',
                ],
                'specifications': {
                    'volume': '50ml',
                    'SPF': '30',
                    'skin type': 'All',
                    'country of origin': 'India',
                }
            },
            {
                'name': 'Car Phone Mount',
                'product_code': 'PROD021',
                'description': (
                    'Magnetic car phone mount with 360-degree rotation, '
                    'compatible with all smartphones'
                ),
                'category': categories.get('AUTO001'),
                'seller': sellers['Tech Solutions Pvt Ltd'],
                'location': locations['Mumbai, Maharashtra'],
                'tag': 'Popular',
                'price': 499.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/carmount1.jpg',
                ],
                'specifications': {
                    'mount type': 'Magnetic',
                    'rotation': '360 degrees',
                    'compatibility': 'All smartphones',
                    'country of origin': 'China',
                }
            },
            {
                'name': 'LEGO Building Set',
                'product_code': 'PROD022',
                'description': (
                    'Creative building blocks set with 500+ pieces, '
                    'perfect for kids and adults'
                ),
                'category': categories.get('TOYS001'),
                'seller': sellers['Book Paradise'],
                'location': locations['Bangalore, Karnataka'],
                'tag': 'Popular',
                'price': 1999.00,
                'currency': 'INR',
                'availability': 'In Stock',
                'images': [
                    'https://example.com/images/lego1.jpg',
                    'https://example.com/images/lego2.jpg',
                ],
                'specifications': {
                    'pieces': '500+',
                    'age group': '6+ years',
                    'country of origin': 'Denmark',
                }
            },
        ]

        products_created = 0
        for prod_data in products_data:
            # Skip if category doesn't exist (for new categories)
            if 'category' in prod_data and prod_data['category'] is None:
                continue
                
            images = prod_data.pop('images', [])
            specifications = prod_data.pop('specifications', {})

            product, created = Product.objects.get_or_create(
                product_code=prod_data['product_code'],
                defaults=prod_data
            )

            if created:
                products_created += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created product: {product.name} '
                        f'({product.product_code})'
                    )
                )

                # Add product images
                for idx, image_url in enumerate(images, start=1):
                    ProductImage.objects.create(
                        product=product,
                        image_url=image_url,
                        order=idx
                    )

                # Add product specifications
                for key, value in specifications.items():
                    ProductSpecification.objects.create(
                        product=product,
                        key=key,
                        value=str(value)
                    )

            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Product already exists: {product.name}'
                    )
                )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Sample data populated successfully!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'   - Categories: {Category.objects.count()}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'   - Sellers: {Seller.objects.count()}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'   - Locations: {Location.objects.count()}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'   - Products: {Product.objects.count()}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'   - Products created in this run: {products_created}'
            )
        )

