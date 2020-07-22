from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required

from account.models import Account
from account.forms import LoginForm, WorkerRegisterForm, CompanyRegisterForm
from account.tokens import account_activation_token
from web_project import settings
from addon.models import GlobalSetting
from addon.decorators import language_scanner
from application.models import Application

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
    user = get_object_or_404(Account, pk=id)
    context = {
        'user': user,
        'applications': Application.objects.filter(user=user).order_by('-apply__user__date_joined'),
    }
    return render(request, 'profile/profile.html', context)


@language_scanner
def LOGIN(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data.get('email'),
                password=form.cleaned_data.get('password')
            )
            if user:
                login(request, user)
                return redirect('account:home')
        else:
            for error in form.errors['__all__']:
                messages.error(request, error)
    context = {
        'form': LoginForm()
    }
    return render(request, 'guest/login.html', context)


@language_scanner
def REGISTER(request):
    if request.method == 'POST':
        if request.POST['user_type'] == 'companyForm':
            form = CompanyRegisterForm(request.POST)
        else:
            form = WorkerRegisterForm(request.POST)
        if form.is_valid():
            user_form = form.save()
            user_form.is_active = False
            user_form.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account.'
            message = render_to_string('settings/active_email.html', {
                'user': user_form,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user_form.pk)),
                'token': account_activation_token.make_token(user_form),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            messages.success(request, _('Please, Check Your Email we\'ve sent an activation link for you Profile.'))
        else:
            messages.error(request, _('Please make sure all the inputs are right!'))

    context = {
        'forms': {
            'workerForm': {'form': WorkerRegisterForm(), 'status': 'active-title-card',
                           'title': 'Registration Account for Worker'},
            'companyForm': {'form': CompanyRegisterForm(), 'status': 'inactive-title-card',
                            'title': 'Registration Account for Company'}
        }
    }
    return render(request, 'guest/register.html', context)


@language_scanner
def LOGOUT(request):
    logout(request)
    return redirect('account:home')


@language_scanner
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = Account.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        Account(request, user)
        return redirect('account:home')
    else:
        return HttpResponse('Activation link is invalid!')
