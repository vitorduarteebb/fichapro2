from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('insumos/', include('insumos.urls')),
    path('receitas/', include('receitas.urls')),
    path('fichas_tecnicas/', include('fichas_tecnicas.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('', include('core.urls')),
   
    path('restaurante/', include('restaurante.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
