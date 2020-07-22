from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.db import transaction

from account.models import Account, Worker, Company


class UserCreationFormExtended(UserCreationForm):
    email = forms.EmailField(label=_('Email'), label_suffix='*', required=True,
                             widget=forms.EmailInput(attrs={
                                 'id': 'EmailInput',
                                 'class': 'form-control',
                                 'placeholder': 'Email',
                             }),
                             error_messages={
                                 'required': _('Double check the submitted Email!'),
                                 'unique': _('This Email is used by another user.'),
                                 'invalid': _('Email is not look like a one!')
                             })
    username = forms.CharField(label=_('Username'), label_suffix='*', required=True,
                               widget=forms.TextInput(attrs={
                                   'id': 'UsernameInput',
                                   'class': 'form-control',
                                   'placeholder': 'Username',
                               }),
                               error_messages={
                                   'required': _('Double check the submitted Username!'),
                                   'unique': _('This Username is used by another user.'),
                                   'invalid': _('Username is not look like a one!')
                               })
    password1 = forms.CharField(label=_('Password'), label_suffix='*', required=True,
                                widget=forms.PasswordInput(attrs={
                                    'id': 'PasswordInput',
                                    'class': 'form-control',
                                    'placeholder': 'Password',
                                    'data_column': '6',
                                    'first': 'true'
                                }),
                                error_messages={
                                    'password_mismatch': _('Passwords are not same.')
                                })

    password2 = forms.CharField(label=_('Re-Write Password'), label_suffix='*', required=True,
                                widget=forms.PasswordInput(attrs={
                                    'id': 'RePasswordInput',
                                    'class': 'form-control',
                                    'placeholder': 'Re-Write Passowrd',
                                    'data_column': '6',
                                    'last': 'true'
                                }))

    class Meta:
        model = Account
        fields = ['email', 'username', 'password1', 'password2']


class WorkerRegisterForm(UserCreationFormExtended):
    first_name = forms.CharField(label=_('First Name'), required=False,
                                 widget=forms.TextInput(attrs={
                                     'id': 'FirstNInput',
                                     'class': 'form-control',
                                     'placeholder': 'First Name',
                                     'autofocus': 'autofocus',
                                     'data_type': 'worker_form',
                                     'data_column': '4',
                                     'first': 'true'
                                 }),
                                 error_messages={
                                     'required': _('Make Sure to fill this input.')
                                 })
    middle_name = forms.CharField(label=_('Middle Name'), required=False,
                                  widget=forms.TextInput(attrs={
                                      'id': 'MiddleNInput',
                                      'class': 'form-control',
                                      'placeholder': 'Middle Name',
                                      'data_column': '4'
                                  }),
                                  error_messages={
                                      'required': _('Make Sure to fill this input.')
                                  })
    last_name = forms.CharField(label=_('Last Name'), required=False,
                                widget=forms.TextInput(attrs={
                                    'id': 'LastNInput',
                                    'class': 'form-control',
                                    'placeholder': 'Last Name',
                                    'data_column': '4',
                                    'last': 'true'
                                }),
                                error_messages={
                                    'required': _('Make Sure to fill this input.')
                                })

    class Meta:
        model = Account
        fields = ['first_name', 'middle_name', 'last_name', 'username', 'email', 'password1',
                  'password2']

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_worker = True
        user.save()
        worker = Worker.objects.create(user=user)
        worker.first_name = self.cleaned_data.get('first_name')
        worker.middle_name = self.cleaned_data.get('middle_name')
        worker.last_name = self.cleaned_data.get('last_name')
        worker.save()
        # student.interests.add(*self.cleaned_data.get('interests'))
        return user


class CompanyRegisterForm(UserCreationFormExtended):
    company_name = forms.CharField(label=_('Company Name'), required=False,
                                   widget=forms.TextInput(attrs={
                                       'id': 'CompanyInput',
                                       'class': 'form-control',
                                       'placeholder': 'Company Name',
                                       'data_type': 'company_form',
                                   }),
                                   error_messages={
                                       'required': _('Make Sure to fill this input.')
                                   })

    class Meta:
        model = Account
        fields = ['company_name', 'username', 'email', 'password1', 'password2']

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_company = True
        user.save()
        company = Company.objects.create(user=user)
        company.company_name = self.cleaned_data.get('company_name')
        company.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label=_('Email'), required=True,
                             widget=forms.EmailInput(attrs={
                                 'id': 'EmailInput',
                                 'class': 'form-control',
                                 'placeholder': 'Email address',
                                 'required': 'required',
                                 'autofocus': 'autofocus'
                             }))
    password = forms.CharField(label=_('Password'), required=True,
                               widget=forms.PasswordInput(attrs={
                                   'id': 'PasswordInput',
                                   'class': 'form-control',
                                   'placeholder': 'Password',
                                   'required': 'required',
                               }))

    class Meta:
        model = Account
        fields = ['email', 'password']

    def clean(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        try:
            user = Account.objects.get(email=email)
        except:
            user = None
        if user is None:
            raise forms.ValidationError(_('We can\'t found any user with that Email!'))
        if not authenticate(email=email, password=password):
            if user is not None and user.is_active:
                raise forms.ValidationError(_('Email or Password is not correct please try again!'))
            raise forms.ValidationError(_('User is not Activated please check you Email'))
