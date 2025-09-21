# nutrition/admin.py (한글화 개선 버전)
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Ingredient, Recipe, RecipeItem

YIELD_PRESETS = {
    "SPONGE": 94, "CHIFFON": 95, "POUND": 92, "BROWNIE": 90, "MUFFIN": 93,
    "BAKED_CHEESE": 93, "NOBAKE_CHEESE": 99, "TART": 90, "TART_SHELL": 88,
    "COOKIE": 85, "MACARON": 90, "CHOUX": 78, "CROISSANT": 91, "BRIOCHE": 93,
    "SHOKUPAN": 92, "BAGUETTE": 89, "CREAM": 99, "CUSTARD": 98, "GANACHE": 99,
}

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('brand', 'name', 'kcal_per100g', 'carbs_per100g', 'protein_per100g', 'fat_per100g', 'get_allergen_display')
    search_fields = ('brand', 'name')
    list_filter = ('contains_milk', 'contains_egg', 'contains_gluten', 'contains_nuts')
    
    fieldsets = [
        ('기본 정보', {
            'fields': ('brand', 'name', 'unit', 'density_g_per_ml'),
            'description': '재료의 기본 정보를 입력하세요.'
        }),
        ('영양성분 (100g당)', {
            'fields': (
                ('kcal_per100g', 'carbs_per100g'),
                ('protein_per100g', 'fat_per100g'),
                ('sugar_per100g', 'sodium_per100g')
            ),
            'description': '100g 기준 영양성분을 입력하세요.'
        }),
        ('알레르기 정보', {
            'fields': (
                ('contains_milk', 'contains_egg'),
                ('contains_gluten', 'contains_nuts'),
                ('contains_soy', 'contains_shellfish')
            ),
            'classes': ['collapse'],
            'description': '해당하는 알레르기 유발요소를 체크하세요.'
        }),
    ]

    def get_allergen_display(self, obj):
        allergens = obj.get_allergens()
        if allergens:
            return format_html(
                '<span style="color: #dc2626; font-weight: 500;">{}</span>',
                ', '.join(allergens)
            )
        return '-'
    get_allergen_display.short_description = '알레르기 정보'

    class Media:
        css = {
            'all': ('admin/nutrition/custom_admin.css',)
        }

class RecipeItemInline(admin.TabularInline):
    model = RecipeItem
    extra = 1
    fields = ('ingredient', 'amount_g', 'amount_ml')
    verbose_name = '재료'
    verbose_name_plural = '레시피 재료'

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'servings', 'piece_weight_g', 'yield_rate', 'get_allergen_display', 'label_buttons')
    list_filter = ('category',)
    search_fields = ('title',)
    
    fieldsets = [
        ('기본 정보', {
            'fields': ('title', 'category', 'notes'),
            'description': '레시피의 기본 정보를 입력하세요.'
        }),
        ('분량 설정', {
            'fields': (
                ('servings', 'piece_weight_g'),
                'yield_rate'
            ),
            'description': '제공 횟수나 1조각 중량을 설정하세요. 수율은 굽기 후 남는 비율입니다.'
        }),
        ('실측 데이터 (선택)', {
            'fields': (
                ('pre_bake_weight_g', 'post_bake_weight_g'),
            ),
            'classes': ['collapse'],
            'description': '실제 측정한 굽기 전후 중량을 입력하면 수율이 자동 계산됩니다.'
        }),
    ]
    
    inlines = [RecipeItemInline]

    def get_allergen_display(self, obj):
        allergens = obj.get_allergens()
        if allergens:
            return format_html(
                '<span style="color: #dc2626; font-weight: 500;">{}</span>',
                ', '.join(allergens)
            )
        return format_html('<span style="color: #48bb78;">없음</span>')
    get_allergen_display.short_description = '알레르기 정보'

    def label_buttons(self, obj):
        """라벨 버튼들"""
        if obj.id:
            html_url = reverse('recipe_label', args=[obj.id])
            pdf_url = reverse('recipe_label_pdf', args=[obj.id])
            
            return format_html(
                '''
                <div class="clean-actions">
                    <a href="{}" target="_blank" class="clean-btn view-btn" title="브라우저에서 라벨 보기">
                        🏷️ 라벨
                    </a>
                    <a href="{}" class="clean-btn pdf-btn" title="PDF 파일로 다운로드">
                        📄 PDF
                    </a>
                </div>
                ''',
                html_url, pdf_url
            )
        return '-'
    
    label_buttons.short_description = '라벨 생성'
    label_buttons.allow_tags = True

    class Media:
        js = ('admin/nutrition/recipe_presets.js',)
        css = {
            'all': ('admin/nutrition/custom_admin.css',)
        }
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['yield_presets'] = YIELD_PRESETS
        return super().changelist_view(request, extra_context)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['yield_presets'] = YIELD_PRESETS
        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)