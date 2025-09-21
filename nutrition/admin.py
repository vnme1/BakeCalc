# nutrition/admin.py (가격 필드 및 원가 버튼 추가)
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
    list_display = ('brand', 'name', 'kcal_per100g', 'price_per_100g', 'get_allergen_display')
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
        ('가격 정보', {
            'fields': ('price_per_100g',),
            'description': '100g 기준 구매 단가를 입력하세요.'
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

    # 👇 이 함수가 새로 추가된 부분입니다!
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['csv_upload_url'] = '/upload/csv/'
        return super().changelist_view(request, extra_context)

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
    list_display = ('title', 'category', 'servings', 'piece_weight_g', 'yield_rate', 'get_allergen_display', 'action_buttons')
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
                'public_id'
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

    def action_buttons(self, obj):
        """액션 버튼들 (라벨, PDF, 원가, QR)"""
        if obj.id:
            label_url = reverse('recipe_label', args=[obj.id])
            pdf_url = reverse('recipe_label_pdf', args=[obj.id])
            
            # public_id가 없으면 생성
            if not obj.public_id:
                obj.save()  # public_id 자동 생성
            
            # QR 관리 페이지로 연결 (공개 페이지가 아닌!)
            qr_management_url = f'/p/{obj.public_id}/qr' if obj.public_id else '#'
            
            return format_html(
                '''
                <div class="clean-actions">
                    <a href="{}" target="_blank" class="clean-btn view-btn" title="브라우저에서 라벨 보기">
                        🏷️ 라벨
                    </a>
                    <a href="{}" class="clean-btn pdf-btn" title="PDF 파일로 다운로드">
                        📄 PDF
                    </a>
                    <a href="#" onclick="showCostInfo({})" class="clean-btn cost-btn" title="원가 정보 보기">
                        💰 원가
                    </a>
                    <a href="{}" target="_blank" class="clean-btn qr-btn" title="QR 코드 관리 페이지">
                        📱 QR
                    </a>
                </div>
                ''',
                label_url, pdf_url, obj.id, qr_management_url
            )
        return '-'
    action_buttons.short_description = '액션'
    action_buttons.allow_tags = True

    class Media:
        js = ('admin/nutrition/recipe_presets.js', 'admin/nutrition/cost_popup.js')
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