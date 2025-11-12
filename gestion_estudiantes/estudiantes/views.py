from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Estudiante, DocumentoEstudiante, Extension, Usuario
from .forms import EstudianteForm, ExtensionForm, UsuarioForm 
from django.db import transaction
from django.contrib.auth.hashers import make_password, check_password

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
    
    return render(request, 'home.html')

# ====================================
# ===== CRUD DE ESTUDIANTES ==========
# ====================================

def listar_estudiantes(request):
    estudiantes = Estudiante.objects.all()
    return render(request, 'listar_estudiantes.html', {'estudiantes': estudiantes})


# ===== REGISTRAR ESTUDIANTE =====
def registrar_estudiante(request):
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
    if not request.session.get('usuario_id'):
        return redirect('login_usuario')

    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == "POST":
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente")
        return redirect('listar_usuarios')

    return render(request, "eliminar_usuario.html", {'usuario': usuario})