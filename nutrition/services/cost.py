# nutrition/services/cost.py
from decimal import Decimal, ROUND_HALF_UP

def _round(v, ndigits=2):
    """원가는 소수점 2자리 반올림"""
    if v is None:
        return 0.0
    q = Decimal('1.' + '0'*ndigits)
    return float(Decimal(v).quantize(q, rounding=ROUND_HALF_UP))

def compute_recipe_cost(recipe, margin_percent=150):
    """
    레시피 원가 계산
    Args:
        recipe: Recipe 객체
        margin_percent: 권장가 마진율 (150 = 50% 마진)
    Returns:
        dict: 총원가, 조각원가, 권장가 정보
    """
    total_cost = Decimal('0')
    
    for item in recipe.items.select_related('ingredient').all():
        ingredient = item.ingredient
        
        # amount_g 계산 (mL → g 변환 포함)
        amt_g = Decimal(item.amount_g or 0)
        if amt_g == 0 and item.amount_ml and ingredient.density_g_per_ml:
            amt_g = Decimal(item.amount_ml) * Decimal(ingredient.density_g_per_ml)
        
        # 재료별 원가 = (사용량g / 100g) * 100g당가격
        ingredient_cost = (amt_g / Decimal('100')) * Decimal(ingredient.price_per_100g or 0)
        total_cost += ingredient_cost
    
    # 손실률 적용 (재료비는 손실률과 관계없이 동일하게 소모됨)
    # 따라서 실제 판매 단위당 원가가 증가함
    yield_scale = Decimal(recipe.yield_rate or 100) / Decimal('100')
    if yield_scale > 0:
        adjusted_total_cost = total_cost / yield_scale
    else:
        adjusted_total_cost = total_cost
    
    # 제공량 계산 (nutrition.py와 동일 로직)
    from .nutrition import compute_recipe_nutrition
    nutrition_data = compute_recipe_nutrition(recipe)
    servings = nutrition_data['servings']
    
    # 조각당 원가
    cost_per_piece = adjusted_total_cost / Decimal(servings) if servings > 0 else Decimal('0')
    
    # 권장 판매가 (마진 적용)
    margin_multiplier = Decimal(margin_percent) / Decimal('100')
    suggested_price_per_piece = cost_per_piece * margin_multiplier
    suggested_total_price = adjusted_total_cost * margin_multiplier
    
    return {
        'total_cost': _round(total_cost),  # 원재료비
        'adjusted_total_cost': _round(adjusted_total_cost),  # 손실률 적용 원가
        'cost_per_piece': _round(cost_per_piece),  # 조각당 원가
        'suggested_price_per_piece': _round(suggested_price_per_piece),  # 권장 조각가
        'suggested_total_price': _round(suggested_total_price),  # 권장 총가격
        'margin_percent': float(margin_percent),
        'yield_rate': float(recipe.yield_rate or 100),
        'servings': servings,
        'items_cost': [
            {
                'ingredient': str(item.ingredient),
                'amount_g': float(amt_g if item == recipe.items.select_related('ingredient').all()[idx] else (
                    Decimal(item.amount_g or 0) if not (item.amount_g == 0 and item.amount_ml and item.ingredient.density_g_per_ml) 
                    else Decimal(item.amount_ml) * Decimal(item.ingredient.density_g_per_ml)
                )),
                'price_per_100g': float(item.ingredient.price_per_100g or 0),
                'cost': _round((
                    Decimal(item.amount_g or 0) if not (item.amount_g == 0 and item.amount_ml and item.ingredient.density_g_per_ml)
                    else Decimal(item.amount_ml) * Decimal(item.ingredient.density_g_per_ml)
                ) / Decimal('100') * Decimal(item.ingredient.price_per_100g or 0))
            }
            for idx, item in enumerate(recipe.items.select_related('ingredient').all())
        ]
    }