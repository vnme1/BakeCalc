# nutrition/serializers.py (기존 코드에 알레르기 정보만 추가)
from rest_framework import serializers
from .models import Ingredient, Recipe, RecipeItem

class IngredientSerializer(serializers.ModelSerializer):
    allergens = serializers.SerializerMethodField()   
    
    class Meta:
        model = Ingredient
        fields = '__all__'
    
    def get_allergens(self, obj):
        return obj.get_allergens()

class RecipeItemSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    ingredient_id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all(), write_only=True
    )

    class Meta:
        model = RecipeItem
        fields = ['id', 'ingredient', 'ingredient_id', 'amount_g', 'amount_ml']

class RecipeSerializer(serializers.ModelSerializer):
    items = RecipeItemSerializer(many=True, read_only=True)
    allergens = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'servings', 'notes', 'piece_weight_g', 'yield_rate', 'items', 'allergens']
    
    def get_allergens(self, obj):
        return obj.get_allergens()