from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin, UnicodeUsernameValidator
)
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractUser

from django_countries.fields import CountryField
from stdimage.validators import MinSizeValidator, MaxSizeValidator
from stdimage.models import StdImageField

import os
from uuid import uuid4

from account.models_addon import UploadToPathAndRename
from account.tasks import process_photo_image
from account.validators import social_url_checker
from web_project.settings import MEDIA_ROOT, STATIC_URL, MEDIA_URL


def image_process(file_name, variations, storage):
    process_photo_image(file_name, variations, storage)
    return False  # prevent default rendering


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_("Users must have an email address"))
        if not username:
            raise ValueError(_("Users must have an username"))

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            **extra_fields
        )

        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        if extra_fields.get('is_admin') is not True:
            raise ValueError(_('Superuser must have is_admin=True.'))

        return self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
            **extra_fields
        )


class Account(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.
    Username and password are required. Other fields are optional.
    """
    username_validator = UnicodeUsernameValidator()
    # Email Field
    email = models.EmailField(
        verbose_name=_('email'),
        max_length=60,
        unique=True,
        help_text=_('Enter valid email: e.g. example@domain.com')
    )
    # Username Field
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[username_validator],
        error_messages={'unique': _("A user with that username already exists."), },
        help_text=_('Enter Username: e.g. Mark99')
    )
    city = models.CharField(max_length=255, default=None, blank=True, null=True)
    country = CountryField(blank_label=_('(select country)'), verbose_name=_('country'), default=None, blank=True,
                           null=True)
    # Data Join, auto add upon the date that created at
    date_joined = models.DateTimeField(
        verbose_name=_('join date'),
        auto_now_add=True
    )
    # Data Join, auto add upon the date that update at
    last_login = models.DateTimeField(
        verbose_name=_('last login'),
        auto_now=True
    )
    
    # Boolean Fields for the authenticatication and the activation, default value is provided for each one
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)
    is_worker = models.BooleanField(default=False)
    # Generated token for user to be used in Global, generated using uuid4
    global_token = models.CharField(max_length=255, default=uuid4)
    profile_pic = StdImageField(
        default='static/default/img/profile.png',
        upload_to=UploadToPathAndRename('upload/img/profile'),
        validators=[
            FileExtensionValidator(['png', 'jpg', 'jpeg', 'PNG', 'JPG']),
            MinSizeValidator(300, 300),
            MaxSizeValidator(1600, 1600)
        ],
        variations={
            'large': (600, 400),
            'thumbnail': (200, 200, True),
            'medium': (300, 200),
        },
        # delete_orphans=True
    )
    cover_pic = StdImageField(
        default='static/default/img/cover.png',
        upload_to=UploadToPathAndRename('upload/img/cover'),
        validators=[
            FileExtensionValidator(['png', 'jpg', 'jpeg', 'PNG', 'JPG']),
            MinSizeValidator(400, 400),
            MaxSizeValidator(2600, 2600)
        ],
        variations={
            'large': (600, 400),
            'thumbnail': (100, 100, True),
            'medium': (300, 200),
        },
        # delete_orphans=True
    )
    bio = models.TextField(blank=True, null=True, max_length=200,
                           default=_('Hey there, I\'m new here can you help with that.'))
    facebook_url = models.URLField(blank=True, null=True, default=None, validators=[social_url_checker])
    twitter_url = models.URLField(blank=True, null=True, default=None, validators=[social_url_checker])
    linkedin_url = models.URLField(blank=True, null=True, default=None, validators=[social_url_checker])
    github_url = models.URLField(blank=True, null=True, default=None, validators=[social_url_checker])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = MyAccountManager()

    def __str__(self):
        return '%s (%s)' % (self.username, self.email)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def is_all_filled(self):
        expect_list = ['facebook_url', 'twitter_url', 'linkedin_url', 'github_url']
        if self.is_company:
            expect_list.extend(['first_name', 'middle_name', 'last_name'])
        else:
            expect_list.append('company_name')
        return all(map(
            lambda x: x[1] is not '' or x[1] is None or x[0] in expect_list,
            self.__dict__.items()
        ))


class Worker(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    # First Name
    first_name = models.CharField(
        verbose_name=_('first name'),
        max_length=150,
        help_text=_('Enter First Name')
    )
    # Middle Name
    middle_name = models.CharField(
        verbose_name=_('middle name'),
        max_length=150,
        help_text=_('Enter Middle Name')
    )
    # Last Name
    last_name = models.CharField(
        verbose_name=_('last name'),
        max_length=150,
        help_text=_('Enter Last Name')
    )
    # Birth Date
    birthday = models.DateTimeField(verbose_name=_('birthday'), default=None, blank=True, null=True)

    nationality = CountryField(blank_label=_('(select nationality)'),
                               verbose_name=_('nationality'),
                               default=None,
                               blank=True,
                               null=True)
    ssid = models.CharField(max_length=255, default=None, blank=True, null=True)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        if not self.middle_name:
            return self.get_short_name()
        else:
            full_name = '%s %s %s' % (self.first_name, self.middle_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        short_name = '%s %s' % (self.first_name, self.last_name)
        return short_name.strip()

    def is_all_filled(self):
        return all(map(
            lambda x: x[1] is not '' and x[1] is not None,
            self.__dict__.items()
        ))


class Company(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    company_name = models.CharField(
        verbose_name=_('company name'),
        max_length=150,
        blank=True,
        help_text=_('Enter Company Name'),
        default=None,
        null=True
    )

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        return self.company_name

    def get_short_name(self):
        """Return the short name for the user."""
        return self.company_name

    def is_all_filled(self):
        return all(map(
            lambda x: x[1] is not '' and x[1] is not None,
            self.__dict__.items()
        ))


