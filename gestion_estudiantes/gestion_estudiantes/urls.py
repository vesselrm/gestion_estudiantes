from django.contrib import admin
from django.urls import path, include
from estudiantes import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_usuario, name='login_usuario'),  # raíz /
    path('', include('estudiantes.urls')),  # incluye todas las demás rutas
]
