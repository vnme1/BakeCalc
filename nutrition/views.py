# nutrition/views.py (PDF 기능 추가)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import Ingredient, Recipe, RecipeItem
from .serializers import IngredientSerializer, RecipeSerializer, RecipeItemSerializer
from .services.nutrition import compute_recipe_nutrition
from .services.pdf import generate_pdf_label, create_pdf_response  # 

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().order_by('brand','name')
    serializer_class = IngredientSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(brand__icontains=q)
        return qs

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    serializer_class = RecipeSerializer

    @action(detail=True, methods=['get'])
    def nutrition(self, request, pk=None):
        recipe = self.get_object()
        data = compute_recipe_nutrition(recipe, precision=1)
        return Response({
            'recipe_id': recipe.id,
            'title': recipe.title,
            'servings': data['servings'],
            'piece_weight_g': data['piece_weight_g'],
            'total_weight_g': data['total_weight_g'],
            'yield_rate': data['yield_rate'],
            'totals': data['totals'],
            'per_serving': data['per_serving'],
            'allergens': recipe.get_allergens(),
        })

    @action(detail=True, methods=['post'])
    def items(self, request, pk=None):
        """레시피에 재료 추가: {ingredient_id, amount_g}"""
        recipe = self.get_object()
        ser = RecipeItemSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save(recipe=recipe)
        return Response(ser.data, status=status.HTTP_201_CREATED)

def recipe_label(request, recipe_id: int):
    """HTML 라벨 뷰 - 알레르기 정보 포함"""
    recipe = get_object_or_404(Recipe.objects.prefetch_related('items__ingredient'), pk=recipe_id)
    nutrition_data = compute_recipe_nutrition(recipe, precision=1)
    allergens = recipe.get_allergens()
    
    context = {
        'recipe': recipe,
        'result': nutrition_data,
        'allergens': allergens,
    }
    return render(request, 'nutrition/label.html', context)

def recipe_label_pdf(request, recipe_id: int):
    """ PDF 라벨 다운로드"""
    recipe = get_object_or_404(Recipe.objects.prefetch_related('items__ingredient'), pk=recipe_id)
    nutrition_data = compute_recipe_nutrition(recipe, precision=1)
    allergens = recipe.get_allergens()
    
    try:
        # PDF 생성
        pdf_data = generate_pdf_label(recipe, nutrition_data, allergens)
        
        # 파일명 생성 (한글 안전하게)
        safe_title = recipe.title.replace(' ', '_').replace('/', '_')[:20]
        filename = f"{safe_title}_영양성분표.pdf"
        
        # PDF 응답 반환
        return create_pdf_response(pdf_data, filename)
        
    except Exception as e:
        # PDF 생성 실패 시 에러 페이지 또는 기본 HTML 반환
        return HttpResponse(f"PDF 생성 중 오류가 발생했습니다: {str(e)}", status=500)