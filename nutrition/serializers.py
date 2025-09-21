# nutrition/serializers.py (가격 정보 추가)
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
    share_url = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'category', 'servings', 'notes', 'piece_weight_g', 
                 'yield_rate', 'public_id', 'items', 'allergens', 'share_url']
    
    def get_allergens(self, obj):
        return obj.get_allergens()
    
    def get_share_url(self, obj):
        if obj.public_id:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/p/{obj.public_id}')
        return None