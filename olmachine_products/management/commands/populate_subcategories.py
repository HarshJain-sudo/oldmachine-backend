"""
Management command to populate subcategories for existing categories.

Usage:
    python manage.py populate_subcategories
"""

from django.core.management.base import BaseCommand
from olmachine_products.models import Category


class Command(BaseCommand):
    """Command to populate subcategories."""

    help = (
        'Populate database with subcategories for existing '
        'top-level categories'
    )

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write(
            self.style.SUCCESS('Starting to populate subcategories...')
        )

        # Define subcategories for each parent category
        subcategories_data = {
            'ELEC001': [  # Electronics
                {
                    'name': 'Mobile Phones',
                    'category_code': 'ELEC001_MOB',
                    'description': 'Smartphones, feature phones, and mobile accessories',
                    'order': 1,
                    'image_url': 'https://example.com/images/mobile-phones.jpg'
                },
                {
                    'name': 'Laptops & Computers',
                    'category_code': 'ELEC001_LAP',
                    'description': 'Laptops, desktops, and computer accessories',
                    'order': 2,
                    'image_url': 'https://example.com/images/laptops.jpg'
                },
                {
                    'name': 'Audio Devices',
                    'category_code': 'ELEC001_AUD',
                    'description': 'Headphones, speakers, and audio equipment',
                    'order': 3,
                    'image_url': 'https://example.com/images/audio.jpg'
                },
                {
                    'name': 'Cameras',
                    'category_code': 'ELEC001_CAM',
                    'description': 'Digital cameras, DSLRs, and camera accessories',
                    'order': 4,
                    'image_url': 'https://example.com/images/cameras.jpg'
                },
            ],
            'FASH001': [  # Fashion
                {
                    'name': "Men's Clothing",
                    'category_code': 'FASH001_MEN',
                    'description': 'Shirts, pants, t-shirts, and men\'s apparel',
                    'order': 1,
                    'image_url': 'https://example.com/images/mens-clothing.jpg'
                },
                {
                    'name': "Women's Clothing",
                    'category_code': 'FASH001_WOM',
                    'description': 'Dresses, tops, bottoms, and women\'s apparel',
                    'order': 2,
                    'image_url': 'https://example.com/images/womens-clothing.jpg'
                },
                {
                    'name': 'Footwear',
                    'category_code': 'FASH001_FOOT',
                    'description': 'Shoes, sandals, and footwear for all',
                    'order': 3,
                    'image_url': 'https://example.com/images/footwear.jpg'
                },
                {
                    'name': 'Accessories',
                    'category_code': 'FASH001_ACC',
                    'description': 'Bags, watches, jewelry, and fashion accessories',
                    'order': 4,
                    'image_url': 'https://example.com/images/accessories.jpg'
                },
            ],
            'HOME001': [  # Home & Kitchen
                {
                    'name': 'Kitchen Appliances',
                    'category_code': 'HOME001_KIT',
                    'description': 'Mixers, blenders, microwaves, and kitchen gadgets',
                    'order': 1,
                    'image_url': 'https://example.com/images/kitchen-appliances.jpg'
                },
                {
                    'name': 'Furniture',
                    'category_code': 'HOME001_FUR',
                    'description': 'Sofas, tables, chairs, and home furniture',
                    'order': 2,
                    'image_url': 'https://example.com/images/furniture.jpg'
                },
                {
                    'name': 'Home Decor',
                    'category_code': 'HOME001_DEC',
                    'description': 'Curtains, rugs, wall art, and decorative items',
                    'order': 3,
                    'image_url': 'https://example.com/images/home-decor.jpg'
                },
                {
                    'name': 'Bedding & Bath',
                    'category_code': 'HOME001_BED',
                    'description': 'Bed sheets, towels, and bathroom essentials',
                    'order': 4,
                    'image_url': 'https://example.com/images/bedding.jpg'
                },
            ],
            'VEH001': [  # Vehicles
                {
                    'name': 'Cars',
                    'category_code': 'VEH001_CAR',
                    'description': 'Sedans, SUVs, hatchbacks, and passenger cars',
                    'order': 1,
                    'image_url': 'https://example.com/images/cars.jpg'
                },
                {
                    'name': 'Motorcycles',
                    'category_code': 'VEH001_BIKE',
                    'description': 'Bikes, scooters, and two-wheelers',
                    'order': 2,
                    'image_url': 'https://example.com/images/motorcycles.jpg'
                },
                {
                    'name': 'Commercial Vehicles',
                    'category_code': 'VEH001_COM',
                    'description': 'Trucks, vans, and commercial vehicles',
                    'order': 3,
                    'image_url': 'https://example.com/images/commercial-vehicles.jpg'
                },
                {
                    'name': 'Vehicle Parts',
                    'category_code': 'VEH001_PARTS',
                    'description': 'Spare parts, accessories, and vehicle components',
                    'order': 4,
                    'image_url': 'https://example.com/images/vehicle-parts.jpg'
                },
            ],
            'SPRT001': [  # Sports & Fitness
                {
                    'name': 'Fitness Equipment',
                    'category_code': 'SPRT001_FIT',
                    'description': 'Gym equipment, weights, and fitness gear',
                    'order': 1,
                    'image_url': 'https://example.com/images/fitness-equipment.jpg'
                },
                {
                    'name': 'Outdoor Sports',
                    'category_code': 'SPRT001_OUT',
                    'description': 'Camping gear, hiking equipment, and outdoor sports',
                    'order': 2,
                    'image_url': 'https://example.com/images/outdoor-sports.jpg'
                },
                {
                    'name': 'Team Sports',
                    'category_code': 'SPRT001_TEAM',
                    'description': 'Cricket, football, basketball equipment',
                    'order': 3,
                    'image_url': 'https://example.com/images/team-sports.jpg'
                },
                {
                    'name': 'Sports Apparel',
                    'category_code': 'SPRT001_APP',
                    'description': 'Sports shoes, activewear, and sports clothing',
                    'order': 4,
                    'image_url': 'https://example.com/images/sports-apparel.jpg'
                },
            ],
            'MACH001': [  # Machinery
                {
                    'name': 'Construction Machinery',
                    'category_code': 'MACH001_CON',
                    'description': 'Excavators, bulldozers, and construction equipment',
                    'order': 1,
                    'image_url': 'https://example.com/images/construction-machinery.jpg'
                },
                {
                    'name': 'Agricultural Machinery',
                    'category_code': 'MACH001_AGR',
                    'description': 'Tractors, harvesters, and farming equipment',
                    'order': 2,
                    'image_url': 'https://example.com/images/agricultural-machinery.jpg'
                },
                {
                    'name': 'Industrial Machinery',
                    'category_code': 'MACH001_IND',
                    'description': 'Manufacturing equipment and industrial machines',
                    'order': 3,
                    'image_url': 'https://example.com/images/industrial-machinery.jpg'
                },
                {
                    'name': 'Machine Tools',
                    'category_code': 'MACH001_TOOL',
                    'description': 'Drills, lathes, and machine tools',
                    'order': 4,
                    'image_url': 'https://example.com/images/machine-tools.jpg'
                },
            ],
            'BOOK001': [  # Books & Media
                {
                    'name': 'Books',
                    'category_code': 'BOOK001_BOOK',
                    'description': 'Fiction, non-fiction, textbooks, and novels',
                    'order': 1,
                    'image_url': 'https://example.com/images/books.jpg'
                },
                {
                    'name': 'E-Books',
                    'category_code': 'BOOK001_EBOOK',
                    'description': 'Digital books and e-readers',
                    'order': 2,
                    'image_url': 'https://example.com/images/ebooks.jpg'
                },
                {
                    'name': 'Music & Movies',
                    'category_code': 'BOOK001_MED',
                    'description': 'CDs, DVDs, and digital media',
                    'order': 3,
                    'image_url': 'https://example.com/images/media.jpg'
                },
                {
                    'name': 'Magazines',
                    'category_code': 'BOOK001_MAG',
                    'description': 'Periodicals, magazines, and journals',
                    'order': 4,
                    'image_url': 'https://example.com/images/magazines.jpg'
                },
            ],
            'BEAU001': [  # Beauty & Personal Care
                {
                    'name': 'Skincare',
                    'category_code': 'BEAU001_SKIN',
                    'description': 'Face creams, lotions, and skincare products',
                    'order': 1,
                    'image_url': 'https://example.com/images/skincare.jpg'
                },
                {
                    'name': 'Makeup',
                    'category_code': 'BEAU001_MAKE',
                    'description': 'Cosmetics, lipsticks, and makeup products',
                    'order': 2,
                    'image_url': 'https://example.com/images/makeup.jpg'
                },
                {
                    'name': 'Hair Care',
                    'category_code': 'BEAU001_HAIR',
                    'description': 'Shampoos, conditioners, and hair products',
                    'order': 3,
                    'image_url': 'https://example.com/images/haircare.jpg'
                },
                {
                    'name': 'Fragrances',
                    'category_code': 'BEAU001_FRAG',
                    'description': 'Perfumes, deodorants, and fragrances',
                    'order': 4,
                    'image_url': 'https://example.com/images/fragrances.jpg'
                },
            ],
            'AUTO001': [  # Automotive
                {
                    'name': 'Car Accessories',
                    'category_code': 'AUTO001_ACC',
                    'description': 'Car covers, seat covers, and car accessories',
                    'order': 1,
                    'image_url': 'https://example.com/images/car-accessories.jpg'
                },
                {
                    'name': 'Car Care',
                    'category_code': 'AUTO001_CARE',
                    'description': 'Car cleaning products and maintenance items',
                    'order': 2,
                    'image_url': 'https://example.com/images/car-care.jpg'
                },
                {
                    'name': 'Car Electronics',
                    'category_code': 'AUTO001_ELEC',
                    'description': 'Car stereos, GPS, and automotive electronics',
                    'order': 3,
                    'image_url': 'https://example.com/images/car-electronics.jpg'
                },
                {
                    'name': 'Tires & Wheels',
                    'category_code': 'AUTO001_TIRE',
                    'description': 'Car tires, wheels, and rims',
                    'order': 4,
                    'image_url': 'https://example.com/images/tires.jpg'
                },
            ],
            'TOYS001': [  # Toys & Games
                {
                    'name': 'Action Figures',
                    'category_code': 'TOYS001_ACT',
                    'description': 'Action figures, dolls, and collectibles',
                    'order': 1,
                    'image_url': 'https://example.com/images/action-figures.jpg'
                },
                {
                    'name': 'Board Games',
                    'category_code': 'TOYS001_BOARD',
                    'description': 'Board games, puzzles, and strategy games',
                    'order': 2,
                    'image_url': 'https://example.com/images/board-games.jpg'
                },
                {
                    'name': 'Educational Toys',
                    'category_code': 'TOYS001_EDU',
                    'description': 'Learning toys and educational games',
                    'order': 3,
                    'image_url': 'https://example.com/images/educational-toys.jpg'
                },
                {
                    'name': 'Outdoor Toys',
                    'category_code': 'TOYS001_OUT',
                    'description': 'Bicycles, scooters, and outdoor play equipment',
                    'order': 4,
                    'image_url': 'https://example.com/images/outdoor-toys.jpg'
                },
            ],
        }

        # Create subcategories
        total_created = 0
        total_updated = 0

        for parent_code, subcategories in subcategories_data.items():
            try:
                parent_category = Category.objects.get(
                    category_code=parent_code
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nProcessing subcategories for: {parent_category.name}'
                    )
                )

                for subcat_data in subcategories:
                    subcategory, created = Category.objects.get_or_create(
                        category_code=subcat_data['category_code'],
                        defaults={
                            **subcat_data,
                            'parent_category': parent_category
                        }
                    )

                    if created:
                        total_created += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ Created: {subcategory.name} '
                                f'({subcategory.category_code})'
                            )
                        )
                    else:
                        # Update existing subcategory if parent changed
                        if subcategory.parent_category != parent_category:
                            subcategory.parent_category = parent_category
                            subcategory.name = subcat_data['name']
                            subcategory.description = subcat_data['description']
                            subcategory.order = subcat_data['order']
                            subcategory.image_url = subcat_data['image_url']
                            subcategory.save()
                            total_updated += 1
                            self.stdout.write(
                                self.style.WARNING(
                                    f'  ↻ Updated: {subcategory.name} '
                                    f'({subcategory.category_code})'
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'  - Already exists: {subcategory.name} '
                                    f'({subcategory.category_code})'
                                )
                            )

            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f'Parent category not found: {parent_code}'
                    )
                )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n\nSummary:'
                f'\n  Created: {total_created} subcategories'
                f'\n  Updated: {total_updated} subcategories'
                f'\n  Total processed: {len(subcategories_data)} parent categories'
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                '\nSubcategories population completed!'
            )
        )

