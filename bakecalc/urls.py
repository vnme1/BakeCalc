from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('nutrition.urls')),     # REST API
    path('', include('nutrition.urls_html')),    # HTML 라벨
]
