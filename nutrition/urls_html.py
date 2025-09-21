# nutrition/urls_html.py (PDF 다운로드 URL 추가)
from django.urls import path
from .views import recipe_label, recipe_label_pdf

urlpatterns = [
    path('recipes/<int:recipe_id>/label', recipe_label, name='recipe_label'),
    path('recipes/<int:recipe_id>/label.pdf', recipe_label_pdf, name='recipe_label_pdf'), 
]