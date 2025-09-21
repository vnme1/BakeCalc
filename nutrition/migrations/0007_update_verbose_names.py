# nutrition/migrations/0007_update_verbose_names.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('nutrition', '0006_add_allergen_fields'),
    ]

    operations = [
        # 이 마이그레이션은 verbose_name 변경만 포함하므로 실제 DB 변경은 없습니다.
        # 단순히 models.py의 verbose_name 변경사항을 기록용으로 생성합니다.
    ]