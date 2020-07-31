from django.urls import path
from django.conf.urls.static import static

from web_project import settings
from account.views import (
    index, profile,
    LOGIN, LOGOUT, REGISTER,
    activate, change_password, update_profile
)

app_name = 'account'

urlpatterns = [
    # View URLs
    path('', index, name='home'),
    path('profile/<int:id>/', profile, name='profile'),
    path('login/', LOGIN, name='login'),
    path('logout/', LOGOUT, name='logout'),
    path('register/', REGISTER, name='register'),
    path('update-password/', change_password, name='update-password'),
    path('update-profile/', update_profile, name='update-profile'),


    # Functional URLs
    path('activate/<uidb64>/<token>', activate, name='activate'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
