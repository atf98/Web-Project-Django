from django.shortcuts import render
from django.utils import translation
from django.shortcuts import get_object_or_404


from web_project import settings

from addon.models import GlobalSetting
from addon.decorators import language_scanner


@language_scanner
def index(request):
    # request.headers
    context = {

    }
    return render(request, 'guest/index.html', context)


@language_scanner
def about(request):
    context = {

    }
    return render(request, 'guest/about.html', context)
