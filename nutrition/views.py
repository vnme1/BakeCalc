from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from .models import Ingredient, Recipe, RecipeItem
from .serializers import IngredientSerializer, RecipeSerializer, RecipeItemSerializer
from .services.nutrition import compute_recipe_nutrition

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
            'piece_weight_g': data['piece_weight_g'],   # ← 추가
            'total_weight_g': data['total_weight_g'],
            'yield_rate': data['yield_rate'],  # ← 추가
            'totals': data['totals'],
            'per_serving': data['per_serving'],
        })

    @action(detail=True, methods=['post'])
    def items(self, request, pk=None):
        """레시피에 재료 추가: {ingredient_id, amount_g}"""
        recipe = self.get_object()
        ser = RecipeItemSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save(recipe=recipe)
        return Response(ser.data, status=status.HTTP_201_CREATED)

# HTML 라벨 뷰
def recipe_label(request, recipe_id: int):
    recipe = get_object_or_404(Recipe.objects.prefetch_related('items__ingredient'), pk=recipe_id)
    comp = compute_recipe_nutrition(recipe, precision=1)
    context = {
        'recipe': recipe,
        'result': comp,
    }
    return render(request, 'nutrition/label.html', context)
