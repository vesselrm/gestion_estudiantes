from django import forms
from .models import Estudiante, Extension, Usuario
import re


class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = [
            'cedula',
            'nombres',
            'apellidos',
            'especialidad',
            'cohorte_mes',
            'cohorte_anio',
            'extension'
        ]
        widgets = {
            'especialidad': forms.Select(attrs={'class': 'form-select'}),
            'cohorte_mes': forms.Select(attrs={'class': 'form-select'}),
            'cohorte_anio': forms.Select(attrs={'class': 'form-select'}),
            'extension': forms.Select(attrs={'class': 'form-select'}),
        }

    # Validación cédula: solo números
    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if not cedula.isdigit():
            raise forms.ValidationError("La cédula solo puede contener números.")
        return cedula

    # Validación nombres: solo letras y espacios
    def clean_nombres(self):
        nombres = self.cleaned_data.get('nombres')
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$', nombres):
            raise forms.ValidationError("El nombre solo puede contener letras y espacios.")
        return nombres

    # Validación apellidos: solo letras y espacios
    def clean_apellidos(self):
        apellidos = self.cleaned_data.get('apellidos')
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$', apellidos):
            raise forms.ValidationError("Los apellidos solo pueden contener letras y espacios.")
        return apellidos


class ExtensionForm(forms.ModelForm):
    class Meta:
        model = Extension
        fields = ['nombre_extension', 'direccion_extension']
        labels = {
            'nombre_extension': 'Nombre de la Extensión',
            'direccion_extension': 'Dirección de la Extensión'
        }


class UsuarioForm(forms.ModelForm):
    contrasena = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese la contraseña'}),
        required=True
    )

    class Meta:
        model = Usuario
        fields = ['nombre_usuario', 'contrasena', 'rol']
        widgets = {
            'nombre_usuario': forms.TextInput(attrs={'placeholder': 'Nombre de usuario'}),
            'rol': forms.Select(),
        }

    def clean_nombre_usuario(self):
        nombre = self.cleaned_data.get('nombre_usuario')
        if Usuario.objects.filter(nombre_usuario=nombre).exists():
            raise forms.ValidationError("Este nombre de usuario ya existe.")
        return nombre

    def clean_contrasena(self):
        contrasena = self.cleaned_data.get('contrasena')
        if len(contrasena) < 6:
            raise forms.ValidationError("La contraseña debe tener al menos 6 caracteres.")
        return contrasena
