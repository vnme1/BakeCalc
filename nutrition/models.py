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
    # 선택: 밀도(g/mL). 없으면 mL 입력 불가 처리/경고
    density_g_per_ml = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)

    class Meta:
        unique_together = [('brand', 'name')]

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
    # ▼ 추가: 1조각(1회 제공) 중량을 직접 지정하고 싶을 때 사용 (선택)
    piece_weight_g = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True)
    yield_rate = models.DecimalField(max_digits=5, decimal_places=2, default=100,
        help_text="굽고 식힌 뒤 남는 비율(%) — 예: 92")
    # 실측 기반 자동계산(선택)
    pre_bake_weight_g = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True)
    post_bake_weight_g = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True)

    def clean(self):
        # 실측값이 둘 다 있으면 yield_rate 자동 산출
        if self.pre_bake_weight_g and self.post_bake_weight_g and float(self.pre_bake_weight_g) > 0:
            self.yield_rate = (float(self.post_bake_weight_g) / float(self.pre_bake_weight_g)) * 100
            
    def __str__(self):
        return self.title

class RecipeItem(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='items')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    amount_g = models.DecimalField(max_digits=9, decimal_places=2)  # 사용량(그램)
    amount_ml = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.recipe} - {self.ingredient} ({self.amount_g}g)"
