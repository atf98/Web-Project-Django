from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinLengthValidator, FileExtensionValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import datetime

import os
import datetime
from stdimage.validators import MinSizeValidator, MaxSizeValidator
from stdimage.models import StdImageField

from account.models import Account
from application.models_addon import CRITERIA_CHOICES
from account.models_addon import UploadToPathAndRename
from web_project.settings import MEDIA_ROOT, MEDIA_URL

GOOGLE_MAP_LINK = 'https://support.google.com/maps/answer/18539?co=GENIE.Platform%3DDesktop&hl=en#6387158'


class Application(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    title = models.CharField(
        verbose_name=_('Title'),
        max_length=255,
        validators=[MinLengthValidator(4)],
        help_text=_('Title for application at least 4 Char')
    )
    body = models.TextField(
        verbose_name=_('Body'),
        help_text=_('You can use HTML tags to style your body.')
    )
    job_title = models.CharField(
        verbose_name=_('Job Title'),
        max_length=255
    )
    place_name = models.CharField(
        verbose_name=_('Work City/State'),
        max_length=255,
        default=_('Not specified yet'),
        help_text=_('Or you can place a Marker down in the map and automatically will add place name.')
    )
    latitude = models.DecimalField(
        verbose_name=_('Latitude'),
        max_digits=30,
        decimal_places=25,
        default=None,
        null=True,
        blank=True,
        help_text=_('Mark any place down from the map to get Location Coordinates.')
    )
    longitude = models.DecimalField(
        verbose_name=_('Longitude'),
        max_digits=30,
        decimal_places=25,
        default=None,
        null=True,
        blank=True,
        help_text=_(
            'Make sure to put the right coordinates (follow this <a href="%s" target="_blank">link</a>)' % GOOGLE_MAP_LINK)
    )
    deadline = models.DateTimeField(
        verbose_name=_('deadline'),
        help_text=_('Note that the end time will be at the midnight of the day you picked.'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return '%s %s' % (self.user.company.company_name, self.title)

    def is_map_placed(self):
        return True if self.latitude and self.longitude else False

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.user.is_all_filled():
            if self.user.is_company:
                # Save current model
                super(Application, self).save(force_insert, force_update, *args, **kwargs)
            else:
                raise ValidationError(_('Only Company Accounts Can Create Applications.'))
        else:
            raise ValidationError(_('Make Sure you did filled all the Data Information for your Account.'))


class ApplicationImage(models.Model):
    application = models.ForeignKey(Application, related_name='images', on_delete=models.CASCADE)
    image = StdImageField(
        default='static/default/img/application.png',
        verbose_name=_('Application Cover'),
        upload_to=UploadToPathAndRename('upload/img/application_cover'),
        validators=[
            FileExtensionValidator(['png', 'jpg', 'jpeg']),
            MinSizeValidator(400, 400),
            MaxSizeValidator(2600, 2600)
        ],
        variations={
            'thumbnail': (100, 100, True),
            'small': (200, 200, True),
            'medium': (526, 375, True),
            'large': (960, 575),
        },
        max_length=255,
        help_text=_('Make sure to add only supported extension: png, jpg and jpeg')
    )
    real_name = models.CharField(verbose_name=_('Real Name'), max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % self.real_name


class ApplicationFile(models.Model):
    application = models.ForeignKey(Application, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(
        verbose_name=_('Application File'),
        upload_to=UploadToPathAndRename('upload/files/applications'),
        validators=[
            FileExtensionValidator(
                ['txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar', ]),
        ],
        max_length=255,
        help_text=_('Make sure to add only supported extension: txt, pdf, docx, xlsx, zip and rar')
    )
    real_name = models.CharField(verbose_name=_('Real Name'), max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s' % self.real_name


class Apply(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    english_skill = models.IntegerField(
        verbose_name=_('English Skill'),
        choices=CRITERIA_CHOICES,
        blank=True,
        null=True
    )
    overall_skill = models.IntegerField(
        verbose_name=_('Overall Skill'),
        choices=CRITERIA_CHOICES,
        blank=True,
        null=True
    )
    leading_skill = models.IntegerField(
        verbose_name=_('Leading Skill'),
        choices=CRITERIA_CHOICES,
        blank=True,
        null=True
    )
    managing_skill = models.IntegerField(
        verbose_name=_('Managing Skill'),
        choices=CRITERIA_CHOICES,
        blank=True,
        null=True
    )
    communication_skill = models.IntegerField(
        verbose_name=_('Communication Skill'),
        choices=CRITERIA_CHOICES,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return '%s %s %s' % (self.user.get_full_name(), _('applied to'), self.application.title)

    def is_all_filled(self):
        return all(map(
            lambda x: x[1] is not '' and x[1] is not None,
            self.__dict__.items()
        ))


class Question(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    question_text = models.CharField(verbose_name=_('Question Text'), max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s %s' % (self.question_text, self.application.title)


class QuestionTaker(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    apply = models.ForeignKey(Apply, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(verbose_name=_('choice text'), max_length=200)

    def __str__(self):
        return '%s %s' % (self.question.question_text, self.choice_text)
