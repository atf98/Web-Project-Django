from django.urls import path
from addon.views import set_language
from web_project import settings
from django.conf.urls.static import static

app_name = 'addon'

urlpatterns = [
    path('set_language/', set_language, name='set_language'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
