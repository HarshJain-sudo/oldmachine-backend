# Generated manually for SavedSearch (buyer saved searches)

import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('olmachine_products', '0005_add_product_listings_indexes'),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedSearch',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False
                )),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('category_code', models.CharField(
                    blank=True, max_length=50, null=True
                )),
                ('query_params', models.JSONField(
                    default=dict,
                    help_text='Filter/sort/search params (e.g. same as search API body)'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='saved_searches',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Saved Search',
                'verbose_name_plural': 'Saved Searches',
                'db_table': 'saved_searches',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='savedsearch',
            index=models.Index(
                fields=['user', '-created_at'],
                name='saved_searc_user_id_created_idx'
            ),
        ),
    ]
