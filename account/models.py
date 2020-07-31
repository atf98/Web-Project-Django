from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin, UnicodeUsernameValidator
)
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

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


def validate_image(size):
    def image_checker(image):
        file_size = image[0].file.size

        limit_mb = size
        if file_size > limit_mb * 1024 * 1024:
            raise ValidationError("Max size of file is %s MB" % limit_mb)

    return image_checker


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
        verbose_name=_('Email'),
        max_length=60,
        unique=True,
        help_text=_('Enter valid email: e.g. example@domain.com')
    )
    # Username Field
    username = models.CharField(
        verbose_name=_('Username'),
        max_length=30,
        unique=True,
        validators=[username_validator],
        error_messages={'unique': _("A user with that username already exists."), },
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. e.g. Mark99')
    )
    city = models.CharField(
        verbose_name=_('City'),
        default=None,
        blank=True,
        null=True,
        max_length=255,
        help_text=_('City/State Can have both, separated by a comma.')
    )
    country = CountryField(
        verbose_name=_('Country'),
        default=None,
        blank=True,
        null=True,
        blank_label=_('(Select Country)'),
    )
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

    # Boolean Fields for the authentication and the activation, default value is provided for each one
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)
    is_worker = models.BooleanField(default=False)

    # Generated token for user to be used in Global, generated using uuid4
    global_token = models.CharField(max_length=255, default=uuid4)
    profile_pic = StdImageField(
        verbose_name=_('Profile Image'),
        default='static/default/img/profile.png',
        upload_to=UploadToPathAndRename('upload/img/profile'),
        validators=[
            FileExtensionValidator(['png', 'jpg', 'jpeg', 'PNG', 'JPG']),
            MinSizeValidator(200, 200),
            MaxSizeValidator(1600, 1600),
        ],
        variations={
            'thumbnail': (40, 40),
            'medium': (200, 200),
            'large': (526, 526),
        },
        help_text=_('Limits:<ul><li>Size 2MB</li><li>Dimensions Range: Width & height (200-1600)</li></ul>')
    )
    cover_pic = StdImageField(
        verbose_name=_('Cover Image'),
        default='static/default/img/cover.png',
        upload_to=UploadToPathAndRename('upload/img/cover'),
        validators=[
            FileExtensionValidator(['png', 'jpg', 'jpeg', 'PNG', 'JPG']),
            MinSizeValidator(400, 400),
            MaxSizeValidator(2600, 2600),
        ],
        variations={
            'medium': (526, 275),
            'large': (960, 553),
        },
        help_text=_('Limits:<ul><li>Size 4MB</li><li>Dimensions Range: Width & height (400-2600)</li></ul>'),
    )
    bio = models.TextField(
        verbose_name=_('Bio'),
        blank=True,
        null=True,
        max_length=200,
        default=_('Hey there, I\'m new here can you help with that.')
    )
    facebook_url = models.URLField(
        verbose_name=_('Facebook URL'),
        blank=True,
        null=True,
        default=None,
        validators=[social_url_checker],
        help_text=_('Link Should look like this: (https://)www.facebook.com/USERNAME/')
    )
    twitter_url = models.URLField(
        verbose_name=_('Twitter URL'),
        blank=True,
        null=True,
        default=None,
        validators=[social_url_checker],
        help_text=_('Link Should look like this: (https://)www.twitter.com/USERNAME/')
    )
    linkedin_url = models.URLField(
        verbose_name=_('LinkedIn URL'),
        blank=True,
        null=True,
        default=None,
        validators=[social_url_checker],
        help_text=_('Link Should look like this: (https://)www.linkedin.com/in/USERNAME/')
    )
    github_url = models.URLField(
        verbose_name=_('GitHub URL'),
        blank=True,
        null=True,
        default=None,
        validators=[social_url_checker],
        help_text=_('Link Should look like this: (https://)www.github.com/USERNAME/')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = MyAccountManager()

    class Meta:
        verbose_name = _('account')
        verbose_name_plural = _('accounts')

    def __str__(self):
        if self.is_worker:
            return '%s %s' % (self.worker.first_name, self.worker.last_name)
        else:
            return '%s' % self.company.company_name

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        if self.is_worker:
            if not self.worker.middle_name:
                return self.get_short_name()
            else:
                full_name = '%s %s %s' % (self.worker.first_name, self.worker.middle_name, self.worker.last_name)
            return full_name.strip()
        else:
            return '%s' % self.company.company_name

    def get_short_name(self):
        """Return the short name for the user."""
        short_name = '%s %s' % (self.worker.first_name, self.worker.last_name)
        return short_name.strip()

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def is_all_filled(self):
        return all(map(
            lambda x: x[1] is not '' or x[1] is None,
            self.__dict__.items()
        ))


class Worker(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    # First Name
    first_name = models.CharField(
        verbose_name=_('First Name'),
        max_length=150,
    )
    # Middle Name
    middle_name = models.CharField(
        verbose_name=_('Middle Name'),
        max_length=150,
    )
    # Last Name
    last_name = models.CharField(
        verbose_name=_('Last Name'),
        max_length=150,
    )
    # Birth Date
    birthday = models.DateTimeField(
        verbose_name=_('Birthday'),
        default=None,
        blank=True,
        null=True
    )

    nationality = CountryField(
        blank_label=_('(Select Nationality)'),
        verbose_name=_('Nationality'),
        default=None,
        blank=True,
        null=True
    )
    ssid = models.CharField(
        max_length=255,
        default=None,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('worker')
        verbose_name_plural = _('workers')

    def is_all_filled(self):
        return all(map(
            lambda x: x[1] is not '' and x[1] is not None,
            self.__dict__.items()
        ))


class Company(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    company_name = models.CharField(
        verbose_name=_('Company Name'),
        max_length=150,
        blank=True,
        help_text=_('Company Name can contain only a-zA-Z, digits and @/./+/-/_'),
        default=None,
        null=True,
    )

    class Meta:
        verbose_name = _('company')
        verbose_name_plural = _('companies')

    def is_all_filled(self):
        return all(map(
            lambda x: x[1] is not '' and x[1] is not None,
            self.__dict__.items()
        ))
