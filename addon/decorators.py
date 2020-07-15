from django.contrib.auth.decorators import user_passes_test, wraps
from django.shortcuts import get_object_or_404
from django.utils import translation

from addon.models import GlobalSetting


def language_scanner(function):
    @wraps(function)
    def decorator(request, *args, **kwargs):
        if request.method == 'GET':
            if GlobalSetting.objects.filter(token=request.session.session_key).exists():
                addon = get_object_or_404(GlobalSetting, token=request.session.session_key)
            else:
                addon = get_object_or_404(GlobalSetting, token=request.user.global_token)
            translation.activate(addon.language)
        return function(request, *args, **kwargs)

    return decorator
