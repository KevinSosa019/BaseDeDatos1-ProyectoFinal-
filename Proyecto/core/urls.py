from django.urls import path
from .views import home, verCursos, crear_curso, register, nosotros, exit_view, busqueda, verUnCurso, editarCurso, eliminarCurso, generar_factura, seleccionar_usuario, matricular_curso
from .views import (
    home, verCursos, crear_curso, register, nosotros, exit_view, busqueda, confirmar_matricula,
    verUnCurso, editarCurso, eliminarCurso,  instructor,buscar_cursos_instructor
)
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('nosotros/', nosotros, name='nosotros'),
    path('logout/', exit_view, name='logout'),
    path('busqueda/', busqueda, name='busqueda'),
    path('verCursos/verUnCurso/<int:id>/', verUnCurso, name='verUnCurso'),
    path('verCursos/editarCurso/<int:id>/', editarCurso, name='editarCurso'),
    path('verCursos/eliminarCurso/<int:id>/', eliminarCurso, name='eliminarCurso'),
    path('generar-factura/', generar_factura, name='generar_factura'),
    path('estudiante/', verCursos, name='estudiante'),
    path('instructor/', instructor, name='instructor'),
    path('instructor/crear_curso/', crear_curso, name='crear_curso'),  # Ruta para crear curso desde instructor
    path('verCursos/', verCursos, name='verCursos'),  # Ruta para listar cursos
    path('verCursos/crear_curso/', crear_curso, name='crear_curso'),  # Ruta para crear curso
    path('estudiante/verUnCurso/<int:id>/', verUnCurso, name='verUnCurso'),
    #path('estudiante/verUnCurso/<int:id>/matricular', verUnCurso, name='verUnCurso'),
    path('instructor/editarCurso/<int:id>/', editarCurso, name='editarCurso'),
    path('instructor/eliminarCurso/<int:id>/', eliminarCurso, name='eliminarCurso'),    
    path('buscar_cursos_instructor/', buscar_cursos_instructor, name='buscar_cursos_instructor'),
    path('generar-factura/', generar_factura, name='generar_factura'),


    path('curso/<int:idCurso>/matricular/', matricular_curso, name='matricular'),
    path('confirmar_matricula/', confirmar_matricula, name='confirmar_matricula'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)