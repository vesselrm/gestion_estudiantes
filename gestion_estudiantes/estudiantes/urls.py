from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_usuario, name='login_usuario'),
    path('logout/', views.logout_usuario, name='logout_usuario'),  # <--- Esto es esencial
    path('home/', views.home, name='home'),
    
    # Estudiantes
    path('estudiantes/', views.listar_estudiantes, name='listar_estudiantes'),
    path('registrar/', views.registrar_estudiante, name='registrar_estudiante'),
    path('editar/<int:pk>/', views.editar_estudiante, name='editar_estudiante'),
    path('detalle/<int:pk>/', views.detalle_estudiante, name='detalle_estudiante'),
    path('eliminar/<int:pk>/', views.eliminar_estudiante, name='eliminar_estudiante'),

    
    path('extensiones/', views.listar_extensiones, name='listar_extensiones'),
    path('extensiones/registrar/', views.registrar_extension, name='registrar_extension'),
    path('extensiones/editar/<int:id>/', views.editar_extension, name='editar_extension'),
    path('extensiones/eliminar/<int:id>/', views.eliminar_extension, name='eliminar_extension'),
    


    # ===== USUARIOS =====
    path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar_usuario'),
    
    
]
