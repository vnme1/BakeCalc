# nutrition/migrations/0006_add_allergen_fields.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('nutrition', '0005_recipe_category_recipe_post_bake_weight_g_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='contains_milk',
            field=models.BooleanField(default=False, verbose_name='유제품'),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='contains_egg',
            field=models.BooleanField(default=False, verbose_name='계란'),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='contains_gluten',
            field=models.BooleanField(default=False, verbose_name='글루텐'),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='contains_nuts',
            field=models.BooleanField(default=False, verbose_name='견과류'),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='contains_soy',
            field=models.BooleanField(default=False, verbose_name='대두'),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='contains_shellfish',
            field=models.BooleanField(default=False, verbose_name='갑각류'),
        ),
    ]