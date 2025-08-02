from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from . import settings
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail import urls as wagtail_urls

urlpatterns = [
    path('wnhelp-back-admin/', admin.site.urls),
    path('api/auth/', include('users_manager.urls')),
    path('cms/', include(wagtailadmin_urls)),
    path('api/', include('wnhelp_api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
