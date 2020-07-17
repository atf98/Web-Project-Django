from django.urls import path
from addon.views import set_language

app_name = 'addon'

urlpatterns = [
    path('set_language/', set_language, name='set_language'),
]
