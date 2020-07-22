from django.urls import path
from django.conf.urls.static import static

from web_project import settings
from account.views import (
    index, about, profile,
    LOGIN, LOGOUT, REGISTER,
    activate
)

app_name = 'account'

urlpatterns = [
    # View URLs
    path('', index, name='home'),
    path('about/', about, name='about'),
    path('profile/<int:id>/', profile, name='profile'),
    path('login/', LOGIN, name='login'),
    path('logout/', LOGOUT, name='logout'),
    path('register/', REGISTER, name='register'),


    # Functional URLs
    path('activate/<uidb64>/<token>', activate, name='activate'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
