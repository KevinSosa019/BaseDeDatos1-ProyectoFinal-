from django.urls import path
from .views import home, products, register, nosotros, exit_view,busqueda
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', home, name='home'),
    path('products/', products, name='products'),
    path('register/', register, name='register'),
    path('nosotros/', nosotros, name='nosotros'),
    path('logout/', exit_view, name='logout'),
    path('busqueda/', busqueda, name='busqueda'),

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
