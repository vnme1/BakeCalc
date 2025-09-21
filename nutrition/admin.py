from django.contrib import admin
from .models import Ingredient, Recipe, RecipeItem

YIELD_PRESETS = {
    "SPONGE": 94, "CHIFFON": 95, "POUND": 92, "BROWNIE": 90, "MUFFIN": 93,
    "BAKED_CHEESE": 93, "NOBAKE_CHEESE": 99, "TART": 90, "TART_SHELL": 88,
    "COOKIE": 85, "MACARON": 90, "CHOUX": 78, "CROISSANT": 91, "BRIOCHE": 93,
    "SHOKUPAN": 92, "BAGUETTE": 89, "CREAM": 99, "CUSTARD": 98, "GANACHE": 99,
}

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('brand','name','kcal_per100g','carbs_per100g','protein_per100g','fat_per100g')
    search_fields = ('brand','name')

class RecipeItemInline(admin.TabularInline):
    model = RecipeItem
    extra = 0
    fields = ('ingredient', 'amount_g', 'amount_ml')  # ← mL도 보이게

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title','category','servings','piece_weight_g','yield_rate')
    fields = ('title','category','servings','piece_weight_g','yield_rate',
              ('pre_bake_weight_g','post_bake_weight_g'),'notes')
    inlines = [RecipeItemInline]

    class Media:  # 카테고리 선택 시 yield_rate 자동 채움
        js = ('admin/nutrition/recipe_presets.js',)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['yield_presets'] = YIELD_PRESETS
        return super().changelist_view(request, extra_context)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['yield_presets'] = YIELD_PRESETS
        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)
