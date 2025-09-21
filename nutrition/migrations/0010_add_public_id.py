# nutrition/migrations/0010_add_public_id.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('nutrition', '0009_add_ingredient_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='public_id',
            field=models.CharField(
                blank=True, 
                max_length=16, 
                unique=True, 
                verbose_name='공개 ID',
                help_text='QR 공유용 고유 ID'
            ),
        ),
    ]