from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.db import transaction
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from account.models import Account, Worker, Company


class UserCreationFormExtended(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': _('Email')})
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': _('Username')})
        self.fields['password1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': _('Password'), 'data_column': '6', 'first': True})
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': _('Password Confirmation'), 'data_column': '6', 'last': True})

    class Meta:
        model = Account
        fields = ['email', 'username', 'password1', 'password2']


class WorkerRegisterForm(UserCreationFormExtended):
    first_name = forms.CharField(label=_('First Name'), required=True,
                                 widget=forms.TextInput(attrs={
                                     'id': 'FirstNInput',
                                     'class': 'form-control',
                                     'placeholder': _('First Name'),
                                     'autofocus': 'autofocus',
                                     'data_type': 'worker_form',
                                     'data_column': '4',
                                     'first': 'true'
                                 }),
                                 error_messages={
                                     'required': _('Make Sure to fill this input.')
                                 })
    middle_name = forms.CharField(label=_('Middle Name'), required=True,
                                  widget=forms.TextInput(attrs={
                                      'id': 'MiddleNInput',
                                      'class': 'form-control',
                                      'placeholder': _('Middle Name'),
                                      'data_column': '4'
                                  }),
                                  error_messages={
                                      'required': _('Make Sure to fill this input.')
                                  })
    last_name = forms.CharField(label=_('Last Name'), required=True,
                                widget=forms.TextInput(attrs={
                                    'id': 'LastNInput',
                                    'class': 'form-control',
                                    'placeholder': _('Last Name'),
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
    company_name = forms.CharField(label=_('Company Name'), required=True,
                                   widget=forms.TextInput(attrs={
                                       'id': 'CompanyInput',
                                       'class': 'form-control',
                                       'placeholder': _('Company Name'),
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
                                 'placeholder': _('Email'),
                                 'required': 'required',
                                 'autofocus': True,
                             }))
    password = forms.CharField(strip=False, label=_('Password'), required=True,
                               widget=forms.PasswordInput(attrs={
                                   'id': 'PasswordInput',
                                   'class': 'form-control',
                                   'placeholder': _('Password'),
                                   'required': 'required',
                               }))
    error_messages = {
        'invalid_login': _(
            "Please enter a correct Email and password. Note that both fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

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


class UpdatePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': _('Old password')})
        self.fields['new_password1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': _('New password')})
        self.fields['new_password1'].help_text = _('''
        <ul>
        <li>Your password can’t be too similar to your other personal information.</li>
        <li>Your password must contain at least 8 characters.</li>
        <li>Your password can’t be a commonly used password.</li>
        <li>Your password can’t be entirely numeric.</li>
        </ul>
        ''')
        self.fields['new_password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': _('Confirm password')})


class SocialMediaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['facebook_url'].widget.attrs.update(
            {'class': 'form-control', 'style': 'direction: ltr;', 'placeholder': _('Facebook URL')})
        self.fields['twitter_url'].widget.attrs.update(
            {'class': 'form-control', 'style': 'direction: ltr;', 'placeholder': _('Twitter URL')})
        self.fields['linkedin_url'].widget.attrs.update(
            {'class': 'form-control', 'style': 'direction: ltr;', 'placeholder': _('LinkedIn URL')})
        self.fields['github_url'].widget.attrs.update(
            {'class': 'form-control', 'style': 'direction: ltr;', 'placeholder': _('GitHub URL')})
        self.fields['facebook_url'].required = False
        self.fields['twitter_url'].required = False
        self.fields['linkedin_url'].required = False
        self.fields['github_url'].required = False

    class Meta:
        model = Account
        fields = ['facebook_url', 'twitter_url', 'linkedin_url', 'github_url']


class AccountUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cover_pic'].widget = forms.FileInput(
            attrs={'class': 'form-control'}
        )
        self.fields['profile_pic'].widget = forms.FileInput(
            attrs={'class': 'form-control'}
        )
        self.fields['country'].widget.attrs.update(
            {'class': 'form-control', 'data_column': '6', 'first': 'true'})
        self.fields['city'].widget.attrs.update(
            {'class': 'form-control', 'data_column': '6', 'last': 'true'})
        self.fields['cover_pic'].widget.attrs.update(
        )
        self.fields['country'].required = False
        self.fields['city'].required = False
        self.fields['cover_pic'].required = False
        self.fields['profile_pic'].required = False

    class Meta:
        model = Account
        fields = ['profile_pic', 'cover_pic', 'country', 'city']


class WorkerUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['birthday'].widget = forms.DateTimeInput(
            attrs={'class': 'form-control datepicker', 'type': 'date'}
        )
        self.fields['ssid'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': _('SSID')}
        )
        self.fields['nationality'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['middle_name'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update(
            {'class': 'form-control'})

    class Meta:
        model = Worker
        fields = ['first_name', 'middle_name', 'last_name', 'nationality', 'birthday', 'ssid']


class CompanyUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company_name'].widget.attrs.update(
            {'class': 'form-control'})
        self.fields['company_name'].required = False

    class Meta:
        model = Company
        fields = ['company_name']


class CoverUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cover_pic'].widget = forms.FileInput(
            attrs={'class': 'form-control', 'onchange': 'loadFile(event,"output_cover")'}
        )

    class Meta:
        model = Account
        fields = ['cover_pic']


class AvatarUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_pic'].widget = forms.FileInput(
            attrs={'class': 'form-control', 'onchange': 'loadFile(event,"output_avatar")'}
        )

    class Meta:
        model = Account
        fields = ['profile_pic']
