from django import forms
from django.core.exceptions import ValidationError
from django.db import connection

class CustomUserCreationForm(forms.Form):
    dni = forms.CharField(max_length=15)
    primer_nombre = forms.CharField(max_length=30)
    segundo_nombre = forms.CharField(max_length=30, required=False)
    apellido1 = forms.CharField(max_length=30)
    apellido2 = forms.CharField(max_length=30, required=False)
    telefono = forms.CharField(max_length=15, required=False)
    correo = forms.EmailField()
    nombre_usuario = forms.CharField(max_length=30)
    contraseña1 = forms.CharField(widget=forms.PasswordInput)
    contraseña2 = forms.CharField(widget=forms.PasswordInput)

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if self.correo_ya_registrado(correo):
            raise ValidationError("Este correo ya está registrado.")
        return correo

    def correo_ya_registrado(self, correo):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM Usuarios WHERE Correo = %s", [correo])
            count = cursor.fetchone()[0]
            return count > 0

    def clean(self):
        cleaned_data = super().clean()
        contraseña1 = cleaned_data.get("contraseña1")
        contraseña2 = cleaned_data.get("contraseña2")
        
        if contraseña1 != contraseña2:
            raise ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data

"""-------------------------------------------------------------------------------------------------"""


class CursoForm(forms.Form):
    IdInstructor = forms.ChoiceField(choices=[])
    IdCategoriaCurso = forms.ChoiceField(choices=[])
    Costo = forms.DecimalField()
    Titulo = forms.CharField(max_length=255)
    Descripcion = forms.CharField(widget=forms.Textarea, required=False)
    FechaInicio = forms.DateField()
    FechaFinal = forms.DateField()

    def __init__(self, *args, **kwargs):
        instructores = kwargs.pop('instructores', [])
        categorias = kwargs.pop('categorias', [])
        super().__init__(*args, **kwargs)
        self.fields['IdInstructor'].choices = instructores
        self.fields['IdCategoriaCurso'].choices = categorias
        
        