from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .views import IngredientViewSet, RecipeViewSet
from .admin import YIELD_PRESETS  # ← admin.py에서 정의한 프리셋 dict import

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
    path('yield-presets/', yield_presets, name='yield-presets'),  # ← 이 줄만 추가
]