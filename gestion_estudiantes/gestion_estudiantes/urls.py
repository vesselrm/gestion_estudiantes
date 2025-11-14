from django.contrib import admin
from django.urls import path, include
from estudiantes import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # raíz /
    path('', include('estudiantes.urls')),  # incluye todas las demás rutas
]
