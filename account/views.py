from urllib.parse import urlparse

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from account.models import Account
from web_project import settings
from addon.models import GlobalSetting
from addon.decorators import language_scanner


@language_scanner
def index(request):

    context = {

    }
    return render(request, 'guest/index.html', context)


@language_scanner
def about(request):

    context = {

    }
    return render(request, 'guest/about.html', context)


@login_required()
@language_scanner
def profile(request, id):
    context = {
        'user': get_object_or_404(Account, pk=id)
    }
    return render(request, 'profile/profile.html', context)

# def youfunc(request):
#     youtemplate = YouModelForm()
#     if request.method == POST:
#         youform = YouModelForm(request.POST, request.FILES)
#         if youform.is_valid():
#             youform.save()
#             return HttpResponseRedirect('http://www.You.url')  # or other
#     youquery =.objects.order_by('user_avatar').last()
#     return render(request, "YouProject/YouHtml.html", {'youtemplate': youtemplate, 'youquery': youquery})
