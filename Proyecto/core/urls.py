from django.urls import path
from .views import (
    home, verCursos, crear_curso, register, nosotros, exit_view, busqueda, 
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
    
    path('estudiante/', verCursos, name='estudiante'),
    path('instructor/', instructor, name='instructor'),
    path('instructor/crear_curso/', crear_curso, name='crear_curso'),  # Ruta para crear curso desde instructor
    
    
    path('verCursos/', verCursos, name='verCursos'),  # Ruta para listar cursos
    path('verCursos/crear_curso/', crear_curso, name='crear_curso'),  # Ruta para crear curso
    
    path('estudiante/verUnCurso/<int:id>/', verUnCurso, name='verUnCurso'),
    path('instructor/editarCurso/<int:id>/', editarCurso, name='editarCurso'),
    path('instructor/eliminarCurso/<int:id>/', eliminarCurso, name='eliminarCurso'),
    
    
    path('buscar_cursos_instructor/', buscar_cursos_instructor, name='buscar_cursos_instructor'),
    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
