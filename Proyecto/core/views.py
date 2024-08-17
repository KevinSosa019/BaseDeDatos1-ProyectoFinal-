from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import connection
from .forms import CustomUserCreationForm, FacturaForm, ConfirmarMatriculaForm
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.db import IntegrityError
from .forms import CursoForm
from django.http import HttpResponseNotFound
from datetime import datetime
from django.utils import timezone



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



"""-----------------------------------------------------------------------"""

def verCursos(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT C.Id, C.Titulo, C.Descripcion, C.Costo, C.FechaInicio, C.FechaFinal,
                   CONCAT_WS(' ', U.Nombre1, U.Nombre2, U.Apellido1, U.Apellido2) AS NombreInstructor
            FROM Cursos C
            JOIN Instructores I ON C.IdInstructor = I.Id
            JOIN Usuarios U ON I.IdUsuario = U.Id
            ORDER BY C.FechaInicio DESC
        """)
        cursos = cursor.fetchall()

    cursos_formateados = []
    for curso in cursos:
        cursos_formateados.append({
            'Id': curso[0],
            'Titulo': curso[1],
            'Descripcion': curso[2],
            'Costo': curso[3],
            'FechaInicio': curso[4],
            'FechaFinal': curso[5],
            'NombreInstructor': curso[6]
        })
    return render(request, 'curso/estudiante.html', {'cursos': cursos_formateados})


def obtener_opciones(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        opciones = cursor.fetchall()
    return [(int(opcion[0]), str(opcion[1])) for opcion in opciones]


def crear_curso(request):
    # Consulta para obtener instructores con nombre completo
    query_instructores = """
    SELECT I.Id, CONCAT_WS(' ', U.Nombre1, U.Nombre2, U.Apellido1, U.Apellido2) AS NombreCompleto
    FROM Instructores I
    JOIN Usuarios U ON I.IdUsuario = U.Id
    """
    opciones_instructor = obtener_opciones(query_instructores)
    
    # Consulta para obtener categorías de cursos
    query_categorias = "SELECT Id, Nombre FROM CategoriaCursos"
    opciones_categoria = obtener_opciones(query_categorias)

    if request.method == 'POST':
        formulario = CursoForm(request.POST, opciones_instructor=opciones_instructor, opciones_categoria=opciones_categoria)
        
        # Imprimir los datos enviados en la solicitud POST
        print("Datos POST:", request.POST)
        
        # Imprimir los errores del formulario para depuración
        print("Formulario válido:", formulario.is_valid())
        print("Errores del formulario:", formulario.errors)
        
        if formulario.is_valid():
            IdInstructor = formulario.cleaned_data['IdInstructor']
            IdCategoriaCurso = formulario.cleaned_data['IdCategoriaCurso']
            Costo = formulario.cleaned_data['Costo']
            Titulo = formulario.cleaned_data['Titulo']
            Descripcion = formulario.cleaned_data['Descripcion']
            FechaInicio = formulario.cleaned_data['FechaInicio']
            FechaFinal = formulario.cleaned_data['FechaFinal']
            
            with connection.cursor() as cursor:
                # Insertar el curso en la base de datos
                cursor.execute("""
                    INSERT INTO Cursos (IdInstructor, IdCategoriaCurso, Costo, Titulo, Descripcion, FechaInicio, FechaFinal)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, [IdInstructor, IdCategoriaCurso, Costo, Titulo, Descripcion, FechaInicio, FechaFinal])
                connection.commit()
            
            return redirect('verCursos')
    else:
        formulario = CursoForm(opciones_instructor=opciones_instructor, opciones_categoria=opciones_categoria)
    
    return render(request, 'curso/crear_curso.html', {'formulario': formulario})


def verUnCurso(request, id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT C.Id, C.Titulo, C.Descripcion, C.Costo, C.FechaInicio, C.FechaFinal,
                   CONCAT_WS(' ', U.Nombre1, U.Nombre2, U.Apellido1, U.Apellido2) AS NombreInstructor
            FROM Cursos C
            JOIN Instructores I ON C.IdInstructor = I.Id
            JOIN Usuarios U ON I.IdUsuario = U.Id
            WHERE C.Id = %s
        """, [id])
        curso = cursor.fetchone()

    usuarios = seleccionar_usuario()

    if curso:
        curso_formateado = {
            'Id': curso[0],
            'Titulo': curso[1],
            'Descripcion': curso[2],
            'Costo': curso[3],
            'FechaInicio': curso[4],
            'FechaFinal': curso[5],
            'NombreInstructor': curso[6]
        }
        return render(request, 'curso/verUnCurso.html', {'curso': curso_formateado , 'usuarios': usuarios})
    else:
        return HttpResponseNotFound("Curso no encontrado")

def eliminarCurso(request, id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM Cursos WHERE Id = %s", [id])
            connection.commit()
        return redirect('verCursos')
    else:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT Titulo FROM Cursos WHERE Id = %s
            """, [id])
            curso = cursor.fetchone()

        if curso:
            return render(request, 'curso/eliminarCurso.html', {'curso': curso[0]})
        else:
            return HttpResponseNotFound("Curso no encontrado")

#def generar_factura(request):
def editarCurso(request, id):
    # Consultar los datos del curso a editar
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Cursos WHERE Id = %s", [id])
        curso = cursor.fetchone()

    if not curso:
        return HttpResponseNotFound("Curso no encontrado.")

    # Consultar opciones para instructores y categorías
    query_instructores = """
    SELECT I.Id, CONCAT_WS(' ', U.Nombre1, U.Nombre2, U.Apellido1, U.Apellido2) AS NombreCompleto
    FROM Instructores I
    JOIN Usuarios U ON I.IdUsuario = U.Id
    """
    opciones_instructor = obtener_opciones(query_instructores)
    
    query_categorias = "SELECT Id, Nombre FROM CategoriaCursos"
    opciones_categoria = obtener_opciones(query_categorias)

    if request.method == 'POST':
        formulario = CursoForm(request.POST, opciones_instructor=opciones_instructor, opciones_categoria=opciones_categoria)
        if formulario.is_valid():
            IdInstructor = formulario.cleaned_data['IdInstructor']
            IdCategoriaCurso = formulario.cleaned_data['IdCategoriaCurso']
            Costo = formulario.cleaned_data['Costo']
            Titulo = formulario.cleaned_data['Titulo']
            Descripcion = formulario.cleaned_data['Descripcion']
            FechaInicio = formulario.cleaned_data['FechaInicio']
            FechaFinal = formulario.cleaned_data['FechaFinal']
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE Cursos
                    SET IdInstructor = %s, IdCategoriaCurso = %s, Costo = %s, Titulo = %s,
                        Descripcion = %s, FechaInicio = %s, FechaFinal = %s
                    WHERE Id = %s
                """, [IdInstructor, IdCategoriaCurso, Costo, Titulo, Descripcion, FechaInicio, FechaFinal, id])
                connection.commit()

            return redirect('instructor')
    else:
        formulario = CursoForm(
            initial={
                'IdInstructor': curso[1],
                'IdCategoriaCurso': curso[2],
                'Costo': curso[3],
                'Titulo': curso[4],
                'Descripcion': curso[5],
                'FechaInicio': curso[6],
                'FechaFinal': curso[7]
            },
            opciones_instructor=opciones_instructor,
            opciones_categoria=opciones_categoria
        )

    return render(request, 'curso/editarCurso.html', {'formulario': formulario})

"""-------------------------------------------------------------------------------------------------"""

def estudiante(request):
    return render(request, 'curso/estudiante.html', {'current_page': 'estudiante'})


def instructor(request):
    return render(request, 'curso/instructor.html', {'current_page': 'instructor'})

def generar_factura(request):
    # Consultar los datos de la factura
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                RTN, Nombre, Domicilio, Telefono, CorreoElectronico,
                Denominacion, FechaLimiteEmision, NumeroCorrelativo, Destino,
                Rango, CAI
            FROM Factura
            WHERE Id = 3
        """)
        factura = cursor.fetchone()

    # Consultar los detalles de la factura si es necesario
    # Aquí puedes añadir consultas adicionales para obtener más detalles.

    if factura:
        (rtn, nombre, domicilio, telefono, correo_electronico,
         denominacion, fecha_limite_emision, numero_correlativo, destino,
         rango, cai) = factura

        # Renderizar la factura usando un template
        context = {
            'nombre': nombre,
            'domicilio': domicilio,
            'telefono': telefono,
            'correo_electronico': correo_electronico,
            'rtn': rtn,
            'cai': cai,
            'numero_correlativo': numero_correlativo,
            'rango': rango,
            'fecha_emision': datetime.now(),
            'fecha_limite_emision': fecha_limite_emision,
            'nombreCliente': 'Juan',
            # Puedes añadir más datos aquí
        }
        return render(request, 'core/Facturacion.html', context)
    else:
        return HttpResponseNotFound("Factura no encontrada", status=404)

"""---------------------------------------------------------------------------------"""

def buscar_cursos_instructor(request):
    if request.method == "POST":
        busqueda = request.POST.get("buscar")

        if busqueda:
            cursos = obtener_cursos_por_instructor(busqueda)
        else:
            cursos = obtener_todos_los_cursos()

        return render(request, 'curso/instructor.html', {'cursos': cursos})
    else:
        return redirect('instructor')

def obtener_cursos_por_instructor(nombre_instructor):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT C.Id, C.Titulo, C.Descripcion, C.Costo, C.FechaInicio, C.FechaFinal,
                   CONCAT_WS(' ', U.Nombre1, U.Nombre2, U.Apellido1, U.Apellido2) AS NombreInstructor
            FROM Cursos C
            JOIN Instructores I ON C.IdInstructor = I.Id
            JOIN Usuarios U ON I.IdUsuario = U.Id
            WHERE CONCAT_WS(' ', U.Nombre1, U.Nombre2, U.Apellido1, U.Apellido2) LIKE %s
            ORDER BY C.FechaInicio DESC
        """, ['%' + nombre_instructor + '%'])
        cursos = cursor.fetchall()

    return [
        {
            'Id': curso[0],
            'Titulo': curso[1],
            'Descripcion': curso[2],
            'Costo': curso[3],
            'FechaInicio': curso[4],
            'FechaFinal': curso[5],
            'NombreInstructor': curso[6]
        } for curso in cursos
    ]

def obtener_todos_los_cursos():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT C.Id, C.Titulo, C.Descripcion, C.Costo, C.FechaInicio, C.FechaFinal,
                   CONCAT_WS(' ', U.Nombre1, U.Nombre2, U.Apellido1, U.Apellido2) AS NombreInstructor
            FROM Cursos C
            JOIN Instructores I ON C.IdInstructor = I.Id
            JOIN Usuarios U ON I.IdUsuario = U.Id
            ORDER BY C.FechaInicio DESC
        """)
        cursos = cursor.fetchall()

    return [
        {
            'Id': curso[0],
            'Titulo': curso[1],
            'Descripcion': curso[2],
            'Costo': curso[3],
            'FechaInicio': curso[4],
            'FechaFinal': curso[5],
            'NombreInstructor': curso[6]
        } for curso in cursos
    ]


def lista_categorias(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM CategoriaCursos")
        categorias = cursor.fetchall()  # Obtenemos todas las filas de la tabla

    return render(request, 'core/Facturacion.html', {'categorias': categorias})

def seleccionar_usuario():
    with connection.cursor() as cursor:
        # Obtener usuarios que no están en la tabla Instructores
        cursor.execute("""
            SELECT u.Id, u.Nombre1, u.Apellido1
            FROM usuarios u 
            LEFT JOIN instructores i ON u.id = i.IdUsuario 
            WHERE i.IdUsuario IS NULL
        """)
        usuarios = cursor.fetchall()

    return usuarios

def matricular_curso(request, idUsuario, idCurso):
    
    return render(request, 'core/matricular.html', {'current_page': 'matricular'})


"""--------------------------------------------------------------------------------------------"""


def matricular_curso(request, idCurso):
    with connection.cursor() as cursor:
        # Obtener las opciones de pago disponibles
        cursor.execute("SELECT Id, Nombre FROM TipoPagos")
        tipo_pagos = cursor.fetchall()

    contexto = {
        'tipo_pagos': tipo_pagos,
        'idCurso': idCurso,
    }

    return render(request, 'matricula/matricular.html', contexto)



def curso_existe(id_curso):
    with connection.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM Cursos WHERE Id = %s', [id_curso])
        return cursor.fetchone()[0] > 0

def usuario_existe(id_usuario):
    with connection.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM Usuarios WHERE Id = %s', [id_usuario])
        return cursor.fetchone()[0] > 0



def obtener_tipo_pagos():
    with connection.cursor() as cursor:
        cursor.execute("SELECT Id, Nombre FROM TipoPagos")
        return cursor.fetchall()



