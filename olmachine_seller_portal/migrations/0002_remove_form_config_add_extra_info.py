# Generated manually - remove CategoryFormConfig/FormField, use extra_info on SellerProduct

from django.db import migrations, models


def copy_form_data_to_extra_info(apps, schema_editor):
    """Copy form_data to extra_info for existing SellerProduct rows."""
    SellerProduct = apps.get_model('olmachine_seller_portal', 'SellerProduct')
    for sp in SellerProduct.objects.all():
        if hasattr(sp, 'form_data') and sp.form_data:
            sp.extra_info = sp.form_data
            sp.save(update_fields=['extra_info'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('olmachine_seller_portal', '0001_initial'),
    ]

    operations = [
        # Add extra_info to SellerProduct
        migrations.AddField(
            model_name='sellerproduct',
            name='extra_info',
            field=models.JSONField(blank=True, default=dict, help_text='Extra product information as key-value JSON'),
        ),
        migrations.RunPython(copy_form_data_to_extra_info, noop_reverse),
        # Remove form_data
        migrations.RemoveField(
            model_name='sellerproduct',
            name='form_data',
        ),
        # Drop FormField first (FK to CategoryFormConfig)
        migrations.DeleteModel(
            name='FormField',
        ),
        migrations.DeleteModel(
            name='CategoryFormConfig',
        ),
    ]
