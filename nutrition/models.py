# nutrition/models.py (help_text 위치 수정)
from django.db import models

class Ingredient(models.Model):
    brand = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=10, default='g')
    kcal_per100g    = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    carbs_per100g   = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    protein_per100g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fat_per100g     = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    sugar_per100g   = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    sodium_per100g  = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    density_g_per_ml = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    
    # 알레르기 정보 필드들
    contains_milk = models.BooleanField(default=False, verbose_name='유제품')
    contains_egg = models.BooleanField(default=False, verbose_name='계란')
    contains_gluten = models.BooleanField(default=False, verbose_name='글루텐')
    contains_nuts = models.BooleanField(default=False, verbose_name='견과류')
    contains_soy = models.BooleanField(default=False, verbose_name='대두')
    contains_shellfish = models.BooleanField(default=False, verbose_name='갑각류')

    class Meta:
        unique_together = [('brand', 'name')]

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
        
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=32, choices=Category.choices, blank=True)
    servings = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True)
    piece_weight_g = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True)
    
    # help_text 제거하여 위치 문제 해결
    yield_rate = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    
    pre_bake_weight_g = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True)
    post_bake_weight_g = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True)

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
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='items')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    amount_g = models.DecimalField(max_digits=9, decimal_places=2)
    amount_ml = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.recipe} - {self.ingredient} ({self.amount_g}g)"