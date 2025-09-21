from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .views import IngredientViewSet, RecipeViewSet, recipe_cost_api
from .admin import YIELD_PRESETS

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'recipes', RecipeViewSet, basename='recipe')

@api_view(['GET'])
def yield_presets(request):
    """
    손실률 프리셋 조회 API
    """
    return Response(YIELD_PRESETS)

urlpatterns = [
    path('', include(router.urls)),
    path('yield-presets/', yield_presets, name='yield-presets'),
    path('recipes/<int:recipe_id>/cost-simple', recipe_cost_api, name='recipe-cost-simple'),
]