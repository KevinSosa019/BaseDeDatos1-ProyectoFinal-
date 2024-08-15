from django.urls import path
from .views import home, verCursos, crear_curso, register, nosotros, exit_view, busqueda, verUnCurso, editarCurso, eliminarCurso
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', home, name='home'),
    path('verCursos/', verCursos, name='verCursos'),  # Ruta para listar cursos
    path('verCursos/crear_curso/', crear_curso, name='crear_curso'),  # Ruta para crear curso
    path('register/', register, name='register'),
    path('nosotros/', nosotros, name='nosotros'),
    path('logout/', exit_view, name='logout'),
    path('busqueda/', busqueda, name='busqueda'),
    
    path('verCursos/verUnCurso/<int:id>/', verUnCurso, name='verUnCurso'),
    path('verCursos/editarCurso/<int:id>/', editarCurso, name='editarCurso'),
    path('verCursos/eliminarCurso/<int:id>/', eliminarCurso, name='eliminarCurso'),

    
]   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
