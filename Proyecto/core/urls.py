from django.urls import path
from .views import home, cursos, register, nosotros, exit_view,busqueda,listar_cursos,crear_curso
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', home, name='home'),
    path('cusos/', cursos, name='cursos'),
    path('register/', register, name='register'),
    path('nosotros/', nosotros, name='nosotros'),
    path('logout/', exit_view, name='logout'),
    path('busqueda/', busqueda, name='busqueda'),
    path('cursos/', listar_cursos, name='listar_cursos'),
    path('cursos/crear/', crear_curso, name='crear_curso'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)