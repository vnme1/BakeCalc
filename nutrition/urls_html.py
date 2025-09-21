# nutrition/urls_html.py
from django.urls import path
from .views import recipe_label, recipe_label_pdf, recipe_public

urlpatterns = [
    path('recipes/<int:recipe_id>/label', recipe_label, name='recipe_label'),
    path('recipes/<int:recipe_id>/label.pdf', recipe_label_pdf, name='recipe_label_pdf'), 
    path('p/<str:public_id>', recipe_public, name='recipe_public'),  # 이 줄이 중요!
]