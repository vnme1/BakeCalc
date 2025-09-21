from django.urls import path
from .views import recipe_label

urlpatterns = [
    path('recipes/<int:recipe_id>/label', recipe_label, name='recipe_label'),
]
