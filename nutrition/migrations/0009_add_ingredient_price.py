# nutrition/migrations/0009_add_ingredient_price.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('nutrition', '0008_alter_ingredient_options_alter_recipe_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='price_per_100g',
            field=models.DecimalField(
                decimal_places=2, 
                default=0, 
                max_digits=10, 
                verbose_name='가격(100g당)',
                help_text='100g 기준 구매 단가 (원)'
            ),
        ),
    ]