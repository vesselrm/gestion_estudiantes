from django.db import models
from django.utils import timezone
from datetime import datetime

# ===== EXTENSIONES =====
class Extension(models.Model):
    nombre_extension = models.CharField(max_length=100)
    direccion_extension = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.nombre_extension


# ===== ESPECIALIDADES =====
class Especialidad(models.Model):
    nombre_especialidad = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre_especialidad


# ===== COHORTES =====
class Cohorte(models.Model):
    MESES = [
        ('Enero', 'Enero'),
        ('Febrero', 'Febrero'),
        ('Marzo', 'Marzo'),
        ('Abril', 'Abril'),
        ('Mayo', 'Mayo'),
        ('Junio', 'Junio'),
        ('Julio', 'Julio'),
        ('Agosto', 'Agosto'),
        ('Septiembre', 'Septiembre'),
        ('Octubre', 'Octubre'),
        ('Noviembre', 'Noviembre'),
        ('Diciembre', 'Diciembre'),
    ]

    # Generar lista de años desde 1900 hasta el actual
    AÑOS = [(str(a), str(a)) for a in range(1900, datetime.now().year + 1)]

    nombre_cohorte = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Cohorte")
    mes = models.CharField(max_length=20, choices=MESES)
    anio = models.CharField(max_length=4, choices=AÑOS)

    class Meta:
        unique_together = ('mes', 'anio')
        verbose_name = "Cohorte"
        verbose_name_plural = "Cohortes"

    def __str__(self):
        return f"{self.nombre_cohorte} ({self.mes} {self.anio})"


# ===== ESTUDIANTES =====
class Estudiante(models.Model):
    cedula = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    cohorte = models.ForeignKey(Cohorte, on_delete=models.CASCADE)
    extension = models.ForeignKey(Extension, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.especialidad} ({self.cohorte})"


# ===== DOCUMENTOS POR ESTUDIANTE =====
class DocumentoEstudiante(models.Model):
    TIPOS_DOCUMENTO = [
        ("Copia de Cédula", "Copia de Cédula"),
        ("Partida de Nacimiento Original", "Partida de Nacimiento Original"),
        ("Fondo Negro Título", "Fondo Negro Título"),
        ("Notas Originales", "Notas Originales"),
        ("Copia de Planilla OPSU", "Copia de Planilla OPSU"),
        ("Copia de Carnet Militar", "Copia de Carnet Militar"),
    ]

    ESTADOS_DOCUMENTO = [
        ("Sí", "Sí"),
        ("No", "No"),
        ("Copia", "Copia"),
        ("Vencida", "Vencida"),
        ("Vacío", "Vacío"),
    ]

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='documentos')
    tipo_documento = models.CharField(max_length=100, choices=TIPOS_DOCUMENTO)
    estado_documento = models.CharField(max_length=50, choices=ESTADOS_DOCUMENTO)
    observacion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.estudiante} - {self.tipo_documento} ({self.estado_documento})"


# ===== USUARIO =====
class Usuario(models.Model):
    nombre_usuario = models.CharField(max_length=100, unique=True)
    contrasena = models.CharField(max_length=128)
    rol = models.CharField(max_length=50, choices=[
        ('Administrador', 'Administrador'),
        ('Secretaria', 'Secretaria'),
        ('Consulta', 'Consulta'),
    ])

    def __str__(self):
        return f"{self.nombre_usuario} ({self.rol})"
