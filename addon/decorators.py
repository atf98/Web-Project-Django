from django.contrib.auth.decorators import user_passes_test, wraps
from django.shortcuts import get_object_or_404
from django.utils import translation
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

from addon.models import GlobalSetting


def worker_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='/login'):
    '''
    Decorator for views that checks that the logged in user is a worker,
    redirects to the log-in page if necessary.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_worker,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def company_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='/login'):
    '''
    Decorator for views that checks that the logged in user is a company,
    redirects to the log-in page if necessary.
    '''
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_company,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def language_scanner(function):
    @wraps(function)
    def decorator(request, *args, **kwargs):
        if not request.user.is_authenticated and not GlobalSetting.objects.filter(
                token=request.session.session_key).exists():
            return function(request, *args, **kwargs)
        elif request.user.is_authenticated and not GlobalSetting.objects.filter(
                token=request.user.global_token).exists():
            return function(request, *args, **kwargs)
        elif GlobalSetting.objects.filter(token=request.session.session_key).exists():
            addon = get_object_or_404(GlobalSetting, token=request.session.session_key)
        else:
            addon = get_object_or_404(GlobalSetting, token=request.user.global_token)
        translation.activate(addon.language)
        return function(request, *args, **kwargs)

    return decorator
