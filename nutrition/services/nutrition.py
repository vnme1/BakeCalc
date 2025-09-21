# nutrition/services/nutrition.py
from decimal import Decimal, ROUND_HALF_UP

FIELDS = ['kcal', 'carbs', 'protein', 'fat', 'sugar', 'sodium']

def _round(v, ndigits=1):
    if v is None:
        return 0.0
    q = Decimal('1.' + '0'*ndigits)
    return float(Decimal(v).quantize(q, rounding=ROUND_HALF_UP))

def compute_recipe_nutrition(recipe, precision=1):
    totals = {k: Decimal('0') for k in FIELDS}
    total_weight = Decimal('0')

    for it in recipe.items.select_related('ingredient').all():
        ing = it.ingredient
        amt_g = Decimal(it.amount_g or 0)

        # amount_g가 0이고 amount_ml이 있는 경우, 밀도로 환산
        if amt_g == 0 and it.amount_ml:
            if ing.density_g_per_ml:
                amt_g = Decimal(it.amount_ml) * Decimal(ing.density_g_per_ml)
            else:
                # 밀도가 없으면 mL 환산 불가 → 0g 처리(라벨에 경고 달고 싶으면 여기서 플래그 세팅)
                amt_g = Decimal('0')

        mul = (amt_g / Decimal('100'))
        totals['kcal']    += mul * Decimal(ing.kcal_per100g)
        totals['carbs']   += mul * Decimal(ing.carbs_per100g)
        totals['protein'] += mul * Decimal(ing.protein_per100g)
        totals['fat']     += mul * Decimal(ing.fat_per100g)
        totals['sugar']   += mul * Decimal(ing.sugar_per100g)
        totals['sodium']  += mul * Decimal(ing.sodium_per100g)
        total_weight      += amt_g

    # ▼ 손실률/증발률 보정 (예: 92%면 scale=0.92)
    scale = (Decimal(recipe.yield_rate or 100) / Decimal('100'))
    if scale != 1:
        for k in totals:
            totals[k] *= scale
        total_weight *= scale

    # ▼ piece_weight_g가 있으면 그것을 우선해 servings 재계산
    piece_w = recipe.piece_weight_g
    if piece_w and piece_w > 0:
        effective_servings = max(int((total_weight / Decimal(piece_w)).quantize(0, ROUND_HALF_UP)), 1)
        effective_piece_g = Decimal(piece_w)
    else:
        effective_servings = max(recipe.servings or 1, 1)
        effective_piece_g = (total_weight / Decimal(effective_servings)) if effective_servings else Decimal('0')

    per_serving = {k: (v/effective_servings) for k, v in totals.items()}

    return {
        'servings': int(effective_servings),
        'piece_weight_g': _round(effective_piece_g, 0),
        'total_weight_g': _round(total_weight, 0),
        'totals': {k: _round(v, precision) for k, v in totals.items()},
        'per_serving': {k: _round(v, precision) for k, v in per_serving.items()},
        'yield_rate': float(scale * 100),  # 보기용
    }
