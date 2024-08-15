from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import connection
from .forms import CustomUserCreationForm
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.db import IntegrityError

def home(request):
    return render(request, 'core/home.html', {'current_page': 'home'})

def cursos(request):
    return render(request, 'curso/cursos.html', {'current_page': 'products'})

def nosotros(request):
    return render(request, 'core/nosotros.html', {'current_page': 'nosotros'})

@login_required
def exit_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return redirect('home')

def busqueda(request):
    return render(request, 'core/busqueda.html', {'current_page': 'busqueda'})

def register(request):
    datos = {
        'formulario': CustomUserCreationForm(),
        'current_page': 'register'
    }
    if request.method == 'POST':
        formulario = CustomUserCreationForm(request.POST)
        if formulario.is_valid():
            # Obtener los datos del formulario
            dni = formulario.cleaned_data['dni']
            nombre1 = formulario.cleaned_data['primer_nombre']
            nombre2 = formulario.cleaned_data['segundo_nombre']
            apellido1 = formulario.cleaned_data['apellido1']
            apellido2 = formulario.cleaned_data['apellido2']
            telefono = formulario.cleaned_data['telefono']
            correo = formulario.cleaned_data['correo']
            nombre_usuario = formulario.cleaned_data['nombre_usuario']
            contrasenia = formulario.cleaned_data['contraseña1']

            if not all([nombre1, apellido1, correo, nombre_usuario, contrasenia, dni]):
                messages.error(request, "Todos los campos son obligatorios.")
                return render(request, 'registration/register.html', {'formulario': formulario})

            if usuario_existe(nombre_usuario):
                formulario.add_error('nombre_usuario', 'Este nombre de usuario ya está en uso.')
                datos['formulario'] = formulario
                return render(request, 'registration/register.html', datos)

            try:
                # Crear el usuario en la base de datos usando SQL directamente
                crear_usuario(dni, nombre1, nombre2, apellido1, apellido2, telefono, correo, nombre_usuario, contrasenia)

                # Autenticar al usuario manualmente usando SQL
                if autenticar_usuario(nombre_usuario, contrasenia):
                    usuario = authenticate(username=nombre_usuario, password=contrasenia)
                    if usuario:
                        login(request, usuario)
                        return redirect('home')
                    else:
                        messages.error(request, 'No se pudo autenticar al usuario.')
                else:
                    messages.error(request, 'Error al autenticar el usuario.')
            except IntegrityError:
                messages.error(request, 'Error al registrar el usuario.')

        else:
            messages.error(request, 'Formulario inválido.')

    else:
        formulario = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'formulario': formulario})


def usuario_existe(nombre_usuario):
    with connection.cursor() as cursor:
        sql = """
        SELECT COUNT(*) FROM Usuarios WHERE NombreUsuario = %s
        """
        cursor.execute(sql, [nombre_usuario])
        count = cursor.fetchone()[0]
        return count > 0

def crear_usuario(dni, primer_nombre, segundo_nombre, apellido1, apellido2, telefono, correo, nombre_usuario, contraseña):
    try:
        with connection.cursor() as cursor:
            contraseña_hash = make_password(contraseña)  # Encriptar la contraseña
            sql = """
            INSERT INTO Usuarios (DNI, Nombre1, Nombre2, Apellido1, Apellido2, Telefono, Correo, NombreUsuario, Contrasenia)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, [dni, primer_nombre, segundo_nombre, apellido1, apellido2, telefono, correo, nombre_usuario, contraseña_hash])
            connection.commit()
            print("Usuario creado exitosamente")  # Para depuración
    except Exception as e:
        print(f"Error al crear el usuario: {e}")  # Para depuración

def autenticar_usuario(nombre_usuario, contrasenia):
    with connection.cursor() as cursor:
        sql = """
        SELECT Contrasenia FROM Usuarios WHERE NombreUsuario = %s
        """
        cursor.execute(sql, [nombre_usuario])
        resultado = cursor.fetchone()
        if resultado:
            stored_password = resultado[0]
            return check_password(contrasenia, stored_password)
        return False

from .forms import CursoForm


"""-----------------------------------------------------------------------"""

def listar_cursos(request):
    cursos = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT C.Id, C.IdInstructor, I.Nombre1, I.Nombre2, I.Apellido1, I.Apellido2, C.Titulo, C.Descripcion, C.Costo, C.FechaInicio, C.FechaFinal
            FROM Cursos C
            JOIN Usuarios I ON C.IdInstructor = I.Id
        """)
        cursos = cursor.fetchall()

    cursos = [
        {
            'Id': curso[0],
            'IdInstructor': {
                'Nombre': f"{curso[2]} {curso[3]} {curso[4]} {curso[5]}"
            },
            'Titulo': curso[6],
            'Descripcion': curso[7],
            'Costo': curso[8],
            'FechaInicio': curso[9],
            'FechaFinal': curso[10]
        } for curso in cursos
    ]
    return render(request, 'curso/cursos.html', {'cursos': cursos})


def crear_curso(request):
    if request.method == 'POST':
        formulario = CursoForm(request.POST)
        print("Formulario inicial:", formulario.data)
        
        if formulario.is_valid():
            print("aqui Formulario valido")

            IdInstructor = formulario.cleaned_data['IdInstructor']
            IdCategoriaCurso = formulario.cleaned_data['IdCategoriaCurso']
            Costo = formulario.cleaned_data['Costo']
            Titulo = formulario.cleaned_data['Titulo']
            Descripcion = formulario.cleaned_data['Descripcion']
            FechaInicio = formulario.cleaned_data['FechaInicio']
            FechaFinal = formulario.cleaned_data['FechaFinal']
            print("Datos del formulario:", IdInstructor, IdCategoriaCurso, Costo, Titulo, Descripcion, FechaInicio, FechaFinal)

            # Verificar que IdInstructor e IdCategoriaCurso existen en la base de datos
            with connection.cursor() as cursor:
                cursor.execute("SELECT Id FROM Instructores WHERE Id = %s", [IdInstructor])
                if not cursor.fetchone():
                    formulario.add_error('IdInstructor', 'Instructor no válido.')
                    print("aqui Instructor")

                cursor.execute("SELECT Id FROM CategoriaCursos WHERE Id = %s", [IdCategoriaCurso])
                if not cursor.fetchone():
                    formulario.add_error('IdCategoriaCurso', 'Categoría de curso no válida.')
                    print("aqui Categoria")

                if formulario.is_valid():
                    cursor.execute("""
                        INSERT INTO Cursos (IdInstructor, IdCategoriaCurso, Costo, Titulo, Descripcion, FechaInicio, FechaFinal)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, [IdInstructor, IdCategoriaCurso, Costo, Titulo, Descripcion, FechaInicio, FechaFinal])
                    connection.commit()
                    return redirect('listar_cursos')
        else:
            print("Errores en el formulario:", formulario.errors)
    else:
        # Obtener opciones para el formulario
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT I.Id, CONCAT_WS(' ', U.Nombre1, U.Nombre2, U.Apellido1, U.Apellido2) AS NombreCompleto
                FROM Instructores I
                JOIN Usuarios U ON I.IdUsuario = U.Id
            """)
            instructores = [(row[0], row[1]) for row in cursor.fetchall()]

            cursor.execute("SELECT Id, Nombre FROM CategoriaCursos")
            categorias = [(row[0], row[1]) for row in cursor.fetchall()]

        formulario = CursoForm(instructores=instructores, categorias=categorias)

    return render(request, 'curso/crear_curso.html', {'formulario': formulario})




