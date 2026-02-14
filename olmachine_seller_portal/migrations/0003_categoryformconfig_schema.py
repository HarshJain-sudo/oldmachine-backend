# Add CategoryFormConfig with schema JSONField (form definition for frontend)

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('olmachine_products', '0002_usercategoryview'),
        ('olmachine_seller_portal', '0002_remove_form_config_add_extra_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryFormConfig',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_active', models.BooleanField(default=True, help_text='Enable/disable form for this category')),
                ('schema', models.JSONField(
                    default=list,
                    help_text='Form schema for frontend: array of {field_name, field_label, field_type, is_required, order, options, ...}'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='form_config',
                    to='olmachine_products.category'
                )),
            ],
            options={
                'verbose_name': 'Category Form Configuration',
                'verbose_name_plural': 'Category Form Configurations',
                'db_table': 'category_form_configs',
            },
        ),
        migrations.AddIndex(
            model_name='categoryformconfig',
            index=models.Index(fields=['category', 'is_active'], name='seller_formconfig_cat_act_idx'),
        ),
    ]
