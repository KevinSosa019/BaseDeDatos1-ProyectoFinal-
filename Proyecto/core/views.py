from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import connection
from .forms import CustomUserCreationForm
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError

def home(request):
    return render(request, 'core/home.html', {'current_page': 'home'})

@login_required
def products(request):
    return render(request, 'core/products.html', {'current_page': 'products'})

def nosotros(request):
    return render(request, 'core/nosotros.html', {'current_page': 'nosotros'})

@login_required
def exit_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    else:
        return redirect('home')

def register(request):
    datos = {
        'formulario': CustomUserCreationForm(),
        'current_page': 'register'
    }

    if request.method == 'POST':
        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            # Obtener los datos del formulario
            nombre_usuario = formulario.cleaned_data['nombre_usuario']
            primer_nombre = formulario.cleaned_data['primer_nombre']
            apellido = formulario.cleaned_data['apellido']
            correo = formulario.cleaned_data['correo']
            contraseña = formulario.cleaned_data['contraseña1']

            # Verificar si el nombre de usuario ya existe
            if usuario_existe(nombre_usuario):
                formulario.add_error('nombre_usuario', 'Este nombre de usuario ya está en uso.')
                datos['formulario'] = formulario
                return render(request, 'registration/register.html', datos)
            try:
                # Crear el usuario en la base de datos usando SQL directamente
                crear_usuario(nombre_usuario, primer_nombre, apellido, correo, contraseña)
                # Autenticar al usuario manualmente usando SQL
                if autenticar_usuario(nombre_usuario, contraseña):
                    usuario = authenticate(username=nombre_usuario, password=contraseña)
                    if usuario:
                        login(request, usuario)
                        return redirect('home')
                    else:
                        formulario.add_error(None, 'No se pudo autenticar al usuario.')
            except IntegrityError:
                formulario.add_error(None, 'Error al registrar el usuario.')

        datos['formulario'] = formulario

    return render(request, 'registration/register.html', datos)

def crear_usuario(nombre_usuario, primer_nombre, apellido, correo, contraseña):
    with connection.cursor() as cursor:
        contraseña_hash = make_password(contraseña)  # Encriptar la contraseña
        sql = """
        INSERT INTO auth_user (username, first_name, last_name, email, password, is_superuser, is_staff, is_active, date_joined)
        VALUES (%s, %s, %s, %s, %s, 0, 0, 1, GETDATE())
        """
        cursor.execute(sql, [nombre_usuario, primer_nombre, apellido, correo, contraseña_hash])
        connection.commit()

def autenticar_usuario(nombre_usuario, contraseña):
    with connection.cursor() as cursor:
        sql = """
        SELECT password FROM auth_user WHERE username = %s
        """
        cursor.execute(sql, [nombre_usuario])
        usuario = cursor.fetchone()
        if usuario:
            hashed_password = usuario[0]
            return check_password(contraseña, hashed_password)
    return False

def usuario_existe(nombre_usuario):
    with connection.cursor() as cursor:
        sql = """
        SELECT COUNT(*) FROM auth_user WHERE username = %s
        """
        cursor.execute(sql, [nombre_usuario])
        count = cursor.fetchone()[0]
        return count > 0

def busqueda(request):
    return render(request, 'core/busqueda.html', {'current_page': 'busqueda'})
