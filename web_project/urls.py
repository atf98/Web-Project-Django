from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('', include('account.urls')),
    path('addons/', include('addon.urls')),
    path('application/', include('application.urls')),
    path('admin/', admin.site.urls),
]

# urlpatterns += i18n_patterns(
#     path('', include('account.urls')),
#     path('admin/', admin.site.urls),
# )
