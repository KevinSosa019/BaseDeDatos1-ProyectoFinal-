from django import forms
from django.core.exceptions import ValidationError
from django.db import connection
from django.contrib.auth.hashers import check_password

class CustomUserCreationForm(forms.Form):
    nombre_usuario = forms.CharField(max_length=150, required=True, label='Nombre de usuario')
    primer_nombre = forms.CharField(max_length=30, required=False, label='Primer nombre')
    apellido = forms.CharField(max_length=30, required=False, label='Apellido')
    correo = forms.EmailField(required=True, label='Correo electrónico')
    contraseña1 = forms.CharField(widget=forms.PasswordInput, required=True, label='Contraseña')
    contraseña2 = forms.CharField(widget=forms.PasswordInput, required=True, label='Confirmar contraseña')

    def clean_correo(self):
        correo = self.cleaned_data['correo']
        if self.correo_ya_registrado(correo):
            raise ValidationError('Este correo electrónico ya está registrado')
        return correo

    def correo_ya_registrado(self, correo):
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM auth_user WHERE email = %s", [correo])
            resultado = cursor.fetchone()[0]
            return resultado > 0

    def clean(self):
        cleaned_data = super().clean()
        contraseña1 = cleaned_data.get("contraseña1")
        contraseña2 = cleaned_data.get("contraseña2")
        if contraseña1 != contraseña2:
            self.add_error('contraseña2', 'Las contraseñas no coinciden')
