# Generated manually for product listings search (filters, sort)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('olmachine_products', '0004_set_initial_category_levels'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['price'], name='prod_price_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['location'], name='prod_location_idx'),
        ),
        migrations.AddIndex(
            model_name='productspecification',
            index=models.Index(
                fields=['product', 'key'],
                name='prodspec_product_key_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='productspecification',
            index=models.Index(
                fields=['product', 'key', 'value'],
                name='prodspec_product_key_val_idx'
            ),
        ),
    ]
