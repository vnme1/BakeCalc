from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import qrcode
from io import BytesIO
import base64
import os
from .models import Ingredient, Recipe, RecipeItem
from .serializers import IngredientSerializer, RecipeSerializer, RecipeItemSerializer
from .services.nutrition import compute_recipe_nutrition
from .services.cost import compute_recipe_cost
from .services.pdf import generate_pdf_label, create_pdf_response
from .services.csv_upload import process_csv_data, bulk_create_ingredients

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

    @action(detail=True, methods=['get'])
    def cost(self, request, pk=None):
        """원가 계산 API"""
        recipe = self.get_object()
        margin = float(request.query_params.get('margin', 150))  # 기본 50% 마진
        cost_data = compute_recipe_cost(recipe, margin_percent=margin)
        
        return Response({
            'recipe_id': recipe.id,
            'title': recipe.title,
            'cost_analysis': cost_data
        })

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """QR 공유용 public_id 생성/조회"""
        recipe = self.get_object()
        if not recipe.public_id:
            recipe.save()  # public_id 자동 생성
        
        return Response({
            'recipe_id': recipe.id,
            'title': recipe.title,
            'public_id': recipe.public_id,
            'share_url': request.build_absolute_uri(f'/p/{recipe.public_id}'),
            'qr_url': request.build_absolute_uri(f'/p/{recipe.public_id}/qr')
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

# def recipe_label_pdf(request, recipe_id: int):
#     """PDF 라벨 다운로드"""
#     recipe = get_object_or_404(Recipe.objects.prefetch_related('items__ingredient'), pk=recipe_id)
#     nutrition_data = compute_recipe_nutrition(recipe, precision=1)
#     allergens = recipe.get_allergens()
    
#     try:
#         pdf_data = generate_pdf_label(recipe, nutrition_data, allergens)
#         safe_title = recipe.title.replace(' ', '_').replace('/', '_')[:20]
#         filename = f"{safe_title}_영양성분표.pdf"
#         return create_pdf_response(pdf_data, filename)
        
#     except Exception as e:
#         return HttpResponse(f"PDF 생성 중 오류가 발생했습니다: {str(e)}", status=500)

# nutrition/views.py에서 recipe_label_pdf 함수만 교체

def recipe_label_pdf(request, recipe_id: int):
    """PDF 라벨 다운로드 - 영문 버전"""
    recipe = get_object_or_404(Recipe.objects.prefetch_related('items__ingredient'), pk=recipe_id)
    nutrition_data = compute_recipe_nutrition(recipe, precision=1)
    allergens = recipe.get_allergens()
    
    try:
        pdf_data = generate_pdf_label(recipe, nutrition_data, allergens)
        
        # 영문 파일명 생성
        safe_title = recipe.title.replace(' ', '_').replace('/', '_')[:30]
        # 특수문자 제거하여 안전한 파일명 생성
        safe_title = ''.join(c for c in safe_title if c.isalnum() or c in '_-')
        
        filename = f"{safe_title}_nutrition_facts.pdf"
        return create_pdf_response(pdf_data, filename)
        
    except Exception as e:
        print(f"PDF 생성 오류: {e}")
        return HttpResponse(f"PDF generation error: {str(e)}", status=500)

def recipe_public(request, public_id: str):
    """공개 라벨 페이지 (QR 공유용)"""
    recipe = get_object_or_404(Recipe.objects.prefetch_related('items__ingredient'), public_id=public_id)
    nutrition_data = compute_recipe_nutrition(recipe, precision=1)
    allergens = recipe.get_allergens()
    
    context = {
        'recipe': recipe,
        'result': nutrition_data,
        'allergens': allergens,
        'is_public': True,
    }
    return render(request, 'nutrition/public_label.html', context)

@api_view(['GET'])
def recipe_cost_api(request, recipe_id: int):
    """원가 계산 전용 API (Admin에서 호출)"""
    recipe = get_object_or_404(Recipe.objects.prefetch_related('items__ingredient'), pk=recipe_id)
    margin = float(request.GET.get('margin', 150))
    cost_data = compute_recipe_cost(recipe, margin_percent=margin)
    return JsonResponse(cost_data)

def recipe_qr_code(request, public_id: str):
    """QR 코드 이미지 생성 및 다운로드"""
    recipe = get_object_or_404(Recipe, public_id=public_id)
    
    # QR 코드에 들어갈 URL (절대 경로)
    qr_url = request.build_absolute_uri(f'/p/{public_id}')
    
    # QR 코드 생성
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    
    # 이미지 생성 (흰 배경, 검은 QR)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # PNG 이미지로 HTTP 응답 생성
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type="image/png")
    response['Content-Disposition'] = f'attachment; filename="{recipe.title}_QR.png"'
    return response

def recipe_qr_page(request, public_id: str):
    """QR 코드 관리 페이지 (미리보기 + 다운로드)"""
    recipe = get_object_or_404(Recipe, public_id=public_id)
    
    # QR URL 생성
    qr_url = request.build_absolute_uri(f'/p/{public_id}')
    qr_image_url = request.build_absolute_uri(f'/p/{public_id}/qr.png')
    
    context = {
        'recipe': recipe,
        'qr_url': qr_url,
        'qr_image_url': qr_image_url,
        'public_id': public_id,
    }
    return render(request, 'nutrition/qr_page.html', context)

@staff_member_required
def csv_upload_page(request):
    """CSV 업로드 페이지"""
    return render(request, 'nutrition/csv_upload.html')

@staff_member_required
@require_http_methods(["POST"])
# @csrf_exempt
def csv_upload_process(request):
    """CSV 파일 처리"""
    
    if 'csv_file' not in request.FILES:
        return JsonResponse({
            'success': False,
            'message': '파일이 선택되지 않았습니다.'
        })
    
    file = request.FILES['csv_file']
    update_existing = request.POST.get('update_existing') == 'true'
    
    # 파일 확장자 검증
    allowed_extensions = ['.csv', '.xlsx', '.xls']
    file_extension = os.path.splitext(file.name)[1].lower()
    
    if file_extension not in allowed_extensions:
        return JsonResponse({
            'success': False,
            'message': 'CSV 또는 Excel 파일만 업로드 가능합니다.'
        })
    
    # 파일 크기 제한 (10MB)
    if file.size > 10 * 1024 * 1024:
        return JsonResponse({
            'success': False,
            'message': '파일 크기는 10MB를 초과할 수 없습니다.'
        })
    
    try:
        # 파일 읽기
        file_content = file.read()
        
        # 데이터 처리
        processed_data, processing_errors = process_csv_data(file_content, file_extension)
        
        if not processed_data and processing_errors:
            return JsonResponse({
                'success': False,
                'message': '파일 처리 중 오류가 발생했습니다.',
                'errors': processing_errors
            })
        
        # 데이터베이스에 저장
        result = bulk_create_ingredients(processed_data, update_existing)
        
        return JsonResponse({
            'success': True,
            'message': f'업로드 완료! 생성: {result["created"]}개, 업데이트: {result["updated"]}개, 건너뜀: {result["skipped"]}개',
            'result': result,
            'processing_errors': processing_errors
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'파일 처리 중 오류가 발생했습니다: {str(e)}'
        })