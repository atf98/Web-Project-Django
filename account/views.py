from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required

from account.models import Account
from account.forms import (
    LoginForm, WorkerRegisterForm, CompanyRegisterForm, UpdatePasswordForm, SocialMediaForm,
    WorkerUpdateForm, AccountUpdateForm, CompanyUpdateForm, CoverUpdateForm, AvatarUpdateForm
)
from account.tokens import account_activation_token
from addon.decorators import language_scanner
from application.models import Application, Apply


@language_scanner
def index(request):
    context = {

    }
    return render(request, 'guest/index.html', context)


@login_required
@language_scanner
def profile(request, id):
    user = get_object_or_404(Account, pk=id)
    context = {
        'user': user,
        'cover_form': CoverUpdateForm(),
        'avatar_form': AvatarUpdateForm(),
    }
    if user.is_worker:
        context['applies'] = Apply.objects.filter(user=user)
        return render(request, 'profile/profile_worker.html', context)
    else:
        context['applications'] = Application.objects.filter(user=user).order_by('-apply__user__date_joined')
        return render(request, 'profile/profile_company.html', context)


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
            mail_subject = _('Activate your blog account.')
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
                           'title': _('Registration Account for Worker')},
            'companyForm': {'form': CompanyRegisterForm(), 'status': 'inactive-title-card',
                            'title': _('Registration Account for Company')}
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
        return HttpResponse(_('Activation link is invalid!'))


@login_required
@language_scanner
def change_password(request):
    if request.method == 'POST':
        form = UpdatePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, _('Your password was successfully updated!'))
            return redirect('account:update-password')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        form = UpdatePasswordForm(request.user)

    context = {
        'form': form
    }
    return render(request, 'settings/change_password.html', context)


@login_required
@language_scanner
def update_profile(request):
    instance = get_object_or_404(Account, id=request.user.id)
    if request.user.is_worker:
        user = WorkerUpdateForm(instance=request.user.worker)
    else:
        user = CompanyUpdateForm(instance=request.user.company)
    social = SocialMediaForm(instance=request.user)
    account = AccountUpdateForm(instance=request.user)

    if request.method == 'POST':
        if request.user.is_worker:
            user = WorkerUpdateForm(request.POST or None, instance=instance)
        else:
            user = CompanyUpdateForm(request.POST or None, instance=instance)
        social = SocialMediaForm(request.POST or None, instance=instance)
        account = AccountUpdateForm(request.POST or None, request.FILES or None, instance=instance)

        if user.is_valid() and social.is_valid() and account.is_valid():
            user.save()
            social.save()
            account.save()
            messages.success(request, _('Edits Saved.'))
        else:
            messages.error(request, _('Please Correct any error down below'))
    context = {
        'forms': [
            {'form': user, 'title': _('Personal Information')},
            {'form': account, 'title': ''},
            {'form': social, 'title': _('Links Settings')},
        ]
    }
    return render(request, 'settings/update_profile.html', context)
