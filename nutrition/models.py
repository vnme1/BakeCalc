# nutrition/models.py (원가 계산 필드 추가)
from django.db import models
from django.utils.crypto import get_random_string
import string

class Ingredient(models.Model):
    brand = models.CharField(max_length=100, blank=True, verbose_name='브랜드')
    name = models.CharField(max_length=200, verbose_name='제품명')
    unit = models.CharField(max_length=10, default='g', verbose_name='단위')
    kcal_per100g = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='칼로리(100g당)')
    carbs_per100g = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='탄수화물(100g당)')
    protein_per100g = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='단백질(100g당)')
    fat_per100g = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='지방(100g당)')
    sugar_per100g = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='당류(100g당)')
    sodium_per100g = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='나트륨(100g당)')
    density_g_per_ml = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, 
                                         verbose_name='밀도(g/mL)', help_text='액체 재료의 밀도 (선택사항)')
    price_per_100g = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                       verbose_name='가격(100g당)', help_text='100g 기준 구매 단가 (원)')
    
    # 알레르기 정보 필드들
    contains_milk = models.BooleanField(default=False, verbose_name='유제품 포함')
    contains_egg = models.BooleanField(default=False, verbose_name='계란 포함')
    contains_gluten = models.BooleanField(default=False, verbose_name='글루텐 포함')
    contains_nuts = models.BooleanField(default=False, verbose_name='견과류 포함')
    contains_soy = models.BooleanField(default=False, verbose_name='대두 포함')
    contains_shellfish = models.BooleanField(default=False, verbose_name='갑각류 포함')

    class Meta:
        unique_together = [('brand', 'name')]
        verbose_name = '재료'
        verbose_name_plural = '재료 목록'

    def get_allergens(self):
        """알레르기 유발요소 목록 반환"""
        allergens = []
        if self.contains_milk: allergens.append('유제품')
        if self.contains_egg: allergens.append('계란')
        if self.contains_gluten: allergens.append('글루텐')
        if self.contains_nuts: allergens.append('견과류')
        if self.contains_soy: allergens.append('대두')
        if self.contains_shellfish: allergens.append('갑각류')
        return allergens

    def __str__(self):
        return f"{self.brand} {self.name}".strip()

def generate_public_id():
    """8자리 랜덤 공개 ID 생성"""
    chars = string.ascii_lowercase + string.digits
    return get_random_string(8, chars)

class Recipe(models.Model):
    class Category(models.TextChoices):
        SPONGE="SPONGE","스폰지/제누와즈"
        CHIFFON="CHIFFON","시폰케이크"
        POUND="POUND","버터/파운드"
        BROWNIE="BROWNIE","브라우니"
        MUFFIN="MUFFIN","머핀"
        BAKED_CHEESE="BAKED_CHEESE","치즈케이크(구움)"
        NOBAKE_CHEESE="NOBAKE_CHEESE","치즈케이크(냉장)"
        TART="TART","타르트/파이"
        TART_SHELL="TART_SHELL","타르트쉘"
        COOKIE="COOKIE","쿠키"
        MACARON="MACARON","마카롱"
        CHOUX="CHOUX","슈"
        CROISSANT="CROISSANT","크루아상/데니시"
        BRIOCHE="BRIOCHE","브리오슈"
        SHOKUPAN="SHOKUPAN","식빵"
        BAGUETTE="BAGUETTE","바게트/하드빵"
        CREAM="CREAM","생크림/크림"
        CUSTARD="CUSTARD","커스터드"
        GANACHE="GANACHE","가나슈/글레이즈"
        
    title = models.CharField(max_length=200, verbose_name='레시피명')
    category = models.CharField(max_length=32, choices=Category.choices, blank=True, verbose_name='카테고리')
    servings = models.PositiveIntegerField(default=1, verbose_name='제공 횟수', 
                                         help_text='총 몇 조각으로 나눌지 입력')
    notes = models.TextField(blank=True, verbose_name='메모')
    piece_weight_g = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, 
                                       verbose_name='1조각 중량(g)', 
                                       help_text='1조각(1회 제공분)의 목표 중량을 입력하면 제공횟수가 자동 계산됩니다')
    yield_rate = models.DecimalField(max_digits=5, decimal_places=2, default=100, 
                                   verbose_name='수율(%)', 
                                   help_text='굽고 식힌 뒤 남는 비율 (예: 92)')
    pre_bake_weight_g = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, 
                                          verbose_name='굽기 전 중량(g)')
    post_bake_weight_g = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, 
                                           verbose_name='굽기 후 중량(g)')
    public_id = models.CharField(max_length=16, unique=True, blank=True, 
                               verbose_name='공개 ID', help_text='QR 공유용 고유 ID')

    class Meta:
        verbose_name = '레시피'
        verbose_name_plural = '레시피 목록'

    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = generate_public_id()
        super().save(*args, **kwargs)

    def get_allergens(self):
        """레시피에 포함된 모든 알레르기 유발요소 반환"""
        allergens = set()
        for item in self.items.select_related('ingredient').all():
            allergens.update(item.ingredient.get_allergens())
        return sorted(allergens)

    def clean(self):
        if self.pre_bake_weight_g and self.post_bake_weight_g and float(self.pre_bake_weight_g) > 0:
            self.yield_rate = (float(self.post_bake_weight_g) / float(self.pre_bake_weight_g)) * 100
            
    def __str__(self):
        return self.title

class RecipeItem(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='items', verbose_name='레시피')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, verbose_name='재료')
    amount_g = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='사용량(g)', 
                                 help_text='그램 단위로 입력')
    amount_ml = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True, 
                                  verbose_name='사용량(mL)', 
                                  help_text='액체 재료의 경우 mL로 입력 (밀도가 입력된 재료만)')

    class Meta:
        verbose_name = '레시피 재료'
        verbose_name_plural = '레시피 재료 목록'

    def __str__(self):
        return f"{self.recipe} - {self.ingredient} ({self.amount_g}g)"