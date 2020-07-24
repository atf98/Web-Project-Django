from django.urls import path
from application.views import (
    index, application, new, add_question, delete, edit, show_apply, complete_apply
)
from web_project import settings
from django.conf.urls.static import static

app_name = 'application'

urlpatterns = [
    # Templates URLs
    path('', index, name='home'),
    path('<int:id>/', application, name='detail'),
    path('add/', new, name='new'),
    path('add-question/<int:id>/', add_question, name='add_question'),
    path('show-apply/<int:id>/', show_apply, name='show_apply'),
    path('complete-apply/<int:id>/', complete_apply, name='complete_apply'),
    path('delete/<int:id>/', delete, name='delete'),
    path('edit/<int:id>/', edit, name='edit'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
