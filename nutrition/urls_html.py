# nutrition/urls_html.py
from django.urls import path
from .views import recipe_label, recipe_label_pdf, recipe_public, recipe_qr_code, recipe_qr_page

urlpatterns = [
    path('recipes/<int:recipe_id>/label', recipe_label, name='recipe_label'),
    path('recipes/<int:recipe_id>/label.pdf', recipe_label_pdf, name='recipe_label_pdf'), 
    path('p/<str:public_id>', recipe_public, name='recipe_public'),
    path('p/<str:public_id>/qr.png', recipe_qr_code, name='recipe_qr_download'),  # QR 이미지 다운로드
    path('p/<str:public_id>/qr', recipe_qr_page, name='recipe_qr_page'),  # QR 관리 페이지
]