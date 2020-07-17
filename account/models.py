from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin, UnicodeUsernameValidator
)
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail

from stdimage.validators import MinSizeValidator, MaxSizeValidator
from stdimage.models import StdImageField

import os
from uuid import uuid4

from account.models_addon import UploadToPathAndRename
from account.tasks import process_photo_image
from web_project.settings import MEDIA_ROOT


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
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')

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
    # First Name
    first_name = models.CharField(
        verbose_name=_('first name'),
        max_length=150,
        blank=True,
        help_text=_('Enter First Name')
    )
    # Last Name
    last_name = models.CharField(
        verbose_name=_('last name'),
        max_length=150,
        blank=True,
        help_text=_('Enter Last Name')
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
    # Boolean Fields for the authenticatication and the activation, default value is provided for each one
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    # Generated token for user to be used in Global, generated using uuid4
    global_token = models.CharField(max_length=255, default=uuid4)
    profile_pic = StdImageField(
        default=os.path.join(MEDIA_ROOT, 'default\\img\\profile.png'),
        upload_to=UploadToPathAndRename(os.path.join(MEDIA_ROOT, 'upload/img', 'profile')),
        validators=[
            FileExtensionValidator(['png', 'jpg', 'jpeg', 'PNG', 'JPG']),
            MinSizeValidator(400, 400),
            MaxSizeValidator(1600, 1600)
        ],
        variations={
            'large': (600, 400),
            'thumbnail': (200, 200, True),
            'medium': (300, 200),
        },
        delete_orphans=True
    )
    cover_pic = StdImageField(
        default=os.path.join(MEDIA_ROOT, 'default\\img\\cover.png'),
        upload_to=UploadToPathAndRename(os.path.join(MEDIA_ROOT, 'upload/img', 'cover')),
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
        delete_orphans=True
        
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
