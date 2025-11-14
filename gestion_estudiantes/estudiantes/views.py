from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Estudiante, DocumentoEstudiante, Extension, Usuario, Cohorte, Especialidad
from .forms import EstudianteForm, ExtensionForm, UsuarioForm, CohorteForm, EspecialidadForm
from django.db import transaction
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Count, Q
from django.http import JsonResponse
import json


def user_role(request):
    return request.session.get('usuario_rol', None)

def solo_admin(request):
    return user_role(request) == "Administrador"

def solo_secretaria(request):
    return user_role(request) == "Secretaria"

def solo_consulta(request):
    return user_role(request) == "Consulta"

# Lista de tipos de documentos y estados
TIPOS_DOCUMENTO = [
    "Copia de Cédula",
    "Partida de Nacimiento Original",
    "Fondo Negro Título",
    "Notas Originales",
    "Copia de Planilla OPSU",
    "Copia de Carnet Militar"
]

ESTADOS_DOCUMENTO = ["Sí", "No", "Copia", "Vencida", "Vacío"]

def home(request):
            # Verificar si hay usuario en sesión
    if not request.session.get('usuario_id'):
        return redirect('login_usuario')
    # Conteo de estudiantes por cohorte
    cohorte_data = Estudiante.objects.values('cohorte__nombre_cohorte').annotate(count=Count('id')).order_by('cohorte__nombre_cohorte')
    cohorte_labels = [item['cohorte__nombre_cohorte'] for item in cohorte_data]
    cohorte_counts = [item['count'] for item in cohorte_data]

    # Conteo de estudiantes por especialidad
    especialidad_data = Estudiante.objects.values('especialidad__nombre_especialidad').annotate(count=Count('id')).order_by('especialidad__nombre_especialidad')
    especialidad_labels = [item['especialidad__nombre_especialidad'] for item in especialidad_data]
    especialidad_counts = [item['count'] for item in especialidad_data]

    context = {
        'cohorte_labels': cohorte_labels,
        'cohorte_counts': cohorte_counts,
        'especialidad_labels': especialidad_labels,
        'especialidad_counts': especialidad_counts,
    }

    return render(request, 'home.html', context)


# ====================================
# ===== CRUD DE ESTUDIANTES ==========
# ====================================

def listar_estudiantes(request):
    estudiantes = Estudiante.objects.all()
    return render(request, 'listar_estudiantes.html', {'estudiantes': estudiantes})


# ===== REGISTRAR ESTUDIANTE =====
def registrar_estudiante(request):
    if solo_consulta(request):
        messages.error(request, "No tienes permisos para agregar estudiantes.")
        return redirect('listar_estudiantes')
    if request.method == 'POST':
        form = EstudianteForm(request.POST)
        if form.is_valid():
            # Guarda el estudiante
            estudiante = form.save()

            # Crear automáticamente los documentos con estado inicial
            for tipo in TIPOS_DOCUMENTO:
                estado = request.POST.get(tipo, "Vacío")
                DocumentoEstudiante.objects.create(
                    estudiante=estudiante,
                    tipo_documento=tipo,
                    estado_documento=estado
                )

            messages.success(request, "✅ Estudiante registrado correctamente.")
            return redirect('listar_estudiantes')
        else:
            messages.error(request, "❌ Corrige los errores en el formulario.")
    else:
        form = EstudianteForm()

    return render(request, 'registrar_estudiante.html', {
        'form': form,
        'tipos': TIPOS_DOCUMENTO,
        'estados': ESTADOS_DOCUMENTO
    })


# ===== EDITAR ESTUDIANTE =====
@transaction.atomic
def editar_estudiante(request, pk):
    if not solo_admin(request):
        messages.error(request, "No tienes permisos para editar estudiantes.")
        return redirect('listar_estudiantes')
    estudiante = get_object_or_404(Estudiante, pk=pk)
    if request.method == 'POST':
        form = EstudianteForm(request.POST, instance=estudiante)
        if form.is_valid():
            form.save()
            # Actualizar estados de documentos
            for tipo in TIPOS_DOCUMENTO:
                estado = request.POST.get(tipo)
                if estado:
                    doc, created = DocumentoEstudiante.objects.get_or_create(
                        estudiante=estudiante, tipo_documento=tipo
                    )
                    doc.estado_documento = estado
                    doc.save()

            messages.success(request, "✅ Estudiante actualizado correctamente.")
            return redirect('listar_estudiantes')
        else:
            messages.error(request, "❌ Corrige los errores en el formulario.")
    else:
        form = EstudianteForm(instance=estudiante)
        documentos = DocumentoEstudiante.objects.filter(estudiante=estudiante)

    return render(request, 'editar_estudiante.html', {
        'form': form,
        'documentos': documentos,
        'estados': ESTADOS_DOCUMENTO
    })


# ===== DETALLE DE ESTUDIANTE =====
def detalle_estudiante(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    documentos = DocumentoEstudiante.objects.filter(estudiante=estudiante)
    return render(request, 'detalle_estudiante.html', {
        'estudiante': estudiante,
        'documentos': documentos
    })


# ===== ELIMINAR ESTUDIANTE =====
def eliminar_estudiante(request, pk):
    if not solo_admin(request):
        messages.error(request, "No tienes permisos para editar estudiantes.")
        return redirect('listar_estudiantes')
    estudiante = get_object_or_404(Estudiante, pk=pk)
    if request.method == 'POST':
        estudiante.delete()
        messages.success(request, "🗑️ Estudiante eliminado correctamente.")
        return redirect('listar_estudiantes')
    return render(request, 'eliminar_estudiante.html', {'estudiante': estudiante})


# ===== LISTAR ESTUDIANTES =====
def listar_estudiantes(request):
    estudiantes = Estudiante.objects.all().order_by('apellidos', 'nombres')
    return render(request, 'listar_estudiantes.html', {
        'estudiantes': estudiantes
    })




# 📋 Listar extensiones
def listar_extensiones(request):
    extensiones = Extension.objects.all()
    return render(request, 'listar_extensiones.html', {'extensiones': extensiones})

# ➕ Registrar nueva extensión
def registrar_extension(request):
    if solo_consulta(request):
        messages.error(request, "No tienes permisos para agregar extensiones.")
        return redirect('listar_extensiones')
    if request.method == 'POST':
        form = ExtensionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Extensión registrada correctamente.')
            return redirect('listar_extensiones')
    else:
        form = ExtensionForm()
    return render(request, 'registrar_extension.html', {'form': form})

# ✏️ Editar extensión existente
def editar_extension(request, id):
    if not solo_admin(request):
        messages.error(request, "No tienes permisos para editar extensiones.")
        return redirect('listar_extensiones')
    extension = get_object_or_404(Extension, id=id)
    if request.method == 'POST':
        form = ExtensionForm(request.POST, instance=extension)
        if form.is_valid():
            form.save()
            messages.success(request, 'Extensión actualizada correctamente.')
            return redirect('listar_extensiones')
    else:
        form = ExtensionForm(instance=extension)
    return render(request, 'editar_extension.html', {'form': form, 'extension': extension})

# ❌ Eliminar extensión
def eliminar_extension(request, id):
    if not solo_admin(request):
        messages.error(request, "No tienes permisos para eliminar extensiones.")
        return redirect('listar_extensiones')
    extension = get_object_or_404(Extension, id=id)
    if request.method == 'POST':
        extension.delete()
        messages.success(request, 'Extensión eliminada correctamente.')
        return redirect('listar_extensiones')
    return render(request, 'eliminar_extension.html', {'extension': extension})

def login_usuario(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre_usuario")
        contrasena = request.POST.get("contrasena")
        print(f"Intento login: {nombre} / {contrasena}")  # DEBUG

        try:
            usuario = Usuario.objects.get(nombre_usuario=nombre)
            if usuario.contrasena == contrasena:
                # Guardar sesión
                request.session['usuario_id'] = usuario.id
                request.session['usuario_nombre'] = usuario.nombre_usuario
                request.session['usuario_rol'] = usuario.rol
                print("Login exitoso")  # DEBUG
                return redirect('home')
            else:
                messages.error(request, "Contraseña incorrecta")
                print("Contraseña incorrecta")  # DEBUG
        except Usuario.DoesNotExist:
            messages.error(request, "El usuario no existe")
            print("Usuario no existe")  # DEBUG

    return render(request, "login.html")



# ===== LOGOUT =====
def logout_usuario(request):
    request.session.flush()  # Borra toda la sesión
    return redirect('login_usuario')  # Redirige al login



# ===== LISTAR USUARIOS =====
def listar_usuarios(request):
    if not request.session.get('usuario_id'):
        return redirect('login_usuario')

    usuarios = Usuario.objects.all()
    return render(request, "listar_usuarios.html", {'usuarios': usuarios})


# ===== CREAR USUARIO =====
def crear_usuario(request):
    if not solo_admin(request):
        messages.error(request, "Solo un administrador puede crear usuarios.")
        return redirect('listar_usuarios')
    if not request.session.get('usuario_id'):
        return redirect('login_usuario')

    if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente")
            return redirect('listar_usuarios')
    else:
        form = UsuarioForm()

    return render(request, "crear_usuario.html", {'form': form})


# ===== EDITAR USUARIO =====
def editar_usuario(request, pk):
    if not solo_admin(request):
        messages.error(request, "Solo un administrador puede crear usuarios.")
        return redirect('listar_usuarios')
    if not request.session.get('usuario_id'):
        return redirect('login_usuario')

    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == "POST":
        # Para evitar error de validación de nombre único al editar
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            # Permitir mantener el mismo nombre de usuario
            form.save()
            messages.success(request, "Usuario actualizado correctamente")
            return redirect('listar_usuarios')
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, "editar_usuario.html", {'form': form, 'usuario': usuario})


# ===== ELIMINAR USUARIO =====
def eliminar_usuario(request, pk):
    if not solo_admin(request):
        messages.error(request, "Solo un administrador puede crear usuarios.")
        return redirect('listar_usuarios')
    if not request.session.get('usuario_id'):
        return redirect('login_usuario')

    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == "POST":
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente")
        return redirect('listar_usuarios')

    return render(request, "eliminar_usuario.html", {'usuario': usuario})


# 📋 Listar cohortes
def listar_cohortes(request):
    cohortes = Cohorte.objects.all().order_by('nombre_cohorte')
    return render(request, 'listar_cohortes.html', {'cohortes': cohortes})

# ➕ Registrar nueva cohorte
def registrar_cohorte(request):
    if solo_consulta(request):
        messages.error(request, "No tienes permisos para agregar cohortes.")
        return redirect('listar_cohortes')
    if request.method == 'POST':
        form = CohorteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Cohorte registrada correctamente.')
            return redirect('listar_cohortes')
        else:
            messages.error(request, '❌ Corrige los errores del formulario.')
    else:
        form = CohorteForm()
    return render(request, 'registrar_cohorte.html', {'form': form})

# ✏️ Editar cohorte existente
def editar_cohorte(request, id):
    if not solo_admin(request):
        messages.error(request, "No tienes permisos para editar cohortes.")
        return redirect('listar_cohortes')
    cohorte = get_object_or_404(Cohorte, id=id)
    if request.method == 'POST':
        form = CohorteForm(request.POST, instance=cohorte)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Cohorte actualizada correctamente.')
            return redirect('listar_cohortes')
        else:
            messages.error(request, '❌ Corrige los errores del formulario.')
    else:
        form = CohorteForm(instance=cohorte)
    return render(request, 'editar_cohorte.html', {'form': form, 'cohorte': cohorte})

# ❌ Eliminar cohorte
def eliminar_cohorte(request, id):
    if not solo_admin(request):
        messages.error(request, "No tienes permisos para eliminar cohortes.")
        return redirect('listar_cohortes')
    cohorte = get_object_or_404(Cohorte, id=id)
    if request.method == 'POST':
        cohorte.delete()
        messages.success(request, '🗑️ Cohorte eliminada correctamente.')
        return redirect('listar_cohortes')
    return render(request, 'eliminar_cohorte.html', {'cohorte': cohorte})


# ====================================
# ===== CRUD DE ESPECIALIDADES =======
# ====================================

# 📋 Listar especialidades
def listar_especialidades(request):
    especialidades = Especialidad.objects.all().order_by('nombre_especialidad')
    return render(request, 'listar_especialidades.html', {'especialidades': especialidades})

# ➕ Registrar nueva especialidad
def registrar_especialidad(request):
    if solo_consulta(request):
        messages.error(request, "No tienes permisos para agregar especialidades.")
        return redirect('listar_especialidades')
    if request.method == 'POST':
        form = EspecialidadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Especialidad registrada correctamente.')
            return redirect('listar_especialidades')
        else:
            messages.error(request, '❌ Corrige los errores del formulario.')
    else:
        form = EspecialidadForm()
    return render(request, 'registrar_especialidad.html', {'form': form})

# ✏️ Editar especialidad existente
def editar_especialidad(request, id):
    if not solo_admin(request):
        messages.error(request, "No tienes permisos para editar especialidades.")
        return redirect('listar_especialidades')
    especialidad = get_object_or_404(Especialidad, id=id)
    if request.method == 'POST':
        form = EspecialidadForm(request.POST, instance=especialidad)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Especialidad actualizada correctamente.')
            return redirect('listar_especialidades')
        else:
            messages.error(request, '❌ Corrige los errores del formulario.')
    else:
        form = EspecialidadForm(instance=especialidad)
    return render(request, 'editar_especialidad.html', {'form': form, 'especialidad': especialidad})

# ❌ Eliminar especialidad
def eliminar_especialidad(request, id):
    if not solo_admin(request):
        messages.error(request, "No tienes permisos para editar especialidades.")
        return redirect('listar_especialidades')
    especialidad = get_object_or_404(Especialidad, id=id)
    if request.method == 'POST':
        especialidad.delete()
        messages.success(request, '🗑️ Especialidad eliminada correctamente.')
        return redirect('listar_especialidades')
    return render(request, 'eliminar_especialidad.html', {'especialidad': especialidad})

# ====================================
# ===== REPORTES ESTADÍSTICOS ========
# ====================================

def reporte_matricula_cohorte(request):
    """
    Cantidad de matrícula (estudiantes inscritos en cada cohorte)
    """
    datos = (
        Estudiante.objects
        .values('cohorte__nombre_cohorte', 'cohorte__mes', 'cohorte__anio')
        .annotate(total=Count('id'))
        .order_by('cohorte__anio', 'cohorte__mes')
    )

    total_general = sum(d['total'] for d in datos)
    contexto = {
        'datos': datos,
        'total_general': total_general
    }
    return render(request, 'reporte_matricula_cohorte.html', contexto)


def reporte_expedientes_completos(request):
    """
    Cantidad y porcentaje de estudiantes con expedientes completos (todos los documentos en 'Sí')
    """
    estudiantes = Estudiante.objects.all()
    total_estudiantes = estudiantes.count()
    completos = 0

    for est in estudiantes:
        documentos = DocumentoEstudiante.objects.filter(estudiante=est)
        if documentos.exists() and all(doc.estado_documento == 'Sí' for doc in documentos):
            completos += 1

    porcentaje = (completos / total_estudiantes * 100) if total_estudiantes > 0 else 0

    contexto = {
        'total_estudiantes': total_estudiantes,
        'completos': completos,
        'porcentaje': round(porcentaje, 2)
    }
    return render(request, 'reporte_expedientes_completos.html', contexto)


def reporte_expedientes_incompletos(request):
    """
    Cantidad y porcentaje de estudiantes con expedientes incompletos 
    (al menos un documento en estado 'No' o 'Vencida')
    """
    estudiantes = Estudiante.objects.all()
    total_estudiantes = estudiantes.count()
    incompletos = 0
    detalle_incompletos = []

    for est in estudiantes:
        documentos = DocumentoEstudiante.objects.filter(estudiante=est)
        # Verificamos si al menos un documento está en 'No' o 'Vencida'
        if documentos.exists() and any(doc.estado_documento in ['No', 'Vencida'] for doc in documentos):
            incompletos += 1
            detalle_incompletos.append(est)

    porcentaje = (incompletos / total_estudiantes * 100) if total_estudiantes > 0 else 0

    contexto = {
        'total_estudiantes': total_estudiantes,
        'incompletos': incompletos,
        'porcentaje': round(porcentaje, 2),
        'detalles': detalle_incompletos  # para mostrar la tabla de detalle
    }
    return render(request, 'reporte_expedientes_incompletos.html', contexto)


def comparativa_especialidad(request):
    """
    Comparativa del total de estudiantes inscritos por especialidad
    """
    datos = (
        Estudiante.objects
        .values('especialidad__nombre_especialidad')
        .annotate(total=Count('id'))
        .order_by('especialidad__nombre_especialidad')
    )

    total_general = sum(d['total'] for d in datos)
    for d in datos:
        d['porcentaje'] = round((d['total'] / total_general * 100), 2) if total_general > 0 else 0

    contexto = {
        'datos': datos,
        'total_general': total_general
    }
    return render(request, 'comparativa_especialidad.html', contexto)


def comparativa_extension(request):
    """
    Comparativa del total de estudiantes inscritos por extensión
    """
    datos = (
        Estudiante.objects
        .values('extension__nombre_extension')
        .annotate(total=Count('id'))
        .order_by('extension__nombre_extension')
    )

    total_general = sum(d['total'] for d in datos)
    for d in datos:
        d['porcentaje'] = round((d['total'] / total_general * 100), 2) if total_general > 0 else 0

    contexto = {
        'datos': datos,
        'total_general': total_general
    }
    return render(request, 'comparativa_extension.html', contexto)

