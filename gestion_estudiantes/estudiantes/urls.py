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
    
    # COHORTE
    path('cohortes/', views.listar_cohortes, name='listar_cohortes'),
    path('cohortes/registrar/', views.registrar_cohorte, name='registrar_cohorte'),
    path('cohortes/editar/<int:id>/', views.editar_cohorte, name='editar_cohorte'),
    path('cohortes/eliminar/<int:id>/', views.eliminar_cohorte, name='eliminar_cohorte'),

    # ESPECIALIDAD
    path('especialidades/', views.listar_especialidades, name='listar_especialidades'),
    path('especialidades/registrar/', views.registrar_especialidad, name='registrar_especialidad'),
    path('especialidades/editar/<int:id>/', views.editar_especialidad, name='editar_especialidad'),
    path('especialidades/eliminar/<int:id>/', views.eliminar_especialidad, name='eliminar_especialidad'),
    
    # --- Reportes estadísticos ---
    path('reportes/matricula-cohorte/', views.reporte_matricula_cohorte, name='reporte_matricula_cohorte'),
    path('reportes/expedientes-completos/', views.reporte_expedientes_completos, name='reporte_expedientes_completos'),
    path('reportes/expedientes-incompletos/', views.reporte_expedientes_incompletos, name='reporte_expedientes_incompletos'),
    path('reportes/comparativa-especialidad/', views.comparativa_especialidad, name='comparativa_especialidad'),
    path('reportes/comparativa-extension/', views.comparativa_extension, name='comparativa_extension'),

    
    
]
