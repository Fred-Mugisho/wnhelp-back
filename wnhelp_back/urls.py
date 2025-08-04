from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from . import settings

urlpatterns = [
    path('wnhelp-back-admin/', admin.site.urls),
    path('api/auth/', include('users_manager.urls')),
    path('api/', include('wnhelp_api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
