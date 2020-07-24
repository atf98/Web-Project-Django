from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

import os
from stdimage.validators import MinSizeValidator, MaxSizeValidator
from stdimage.models import StdImageField

from account.models import Account
from application.models_addon import CRITERIA_CHOICES
from account.models_addon import UploadToPathAndRename
from web_project.settings import MEDIA_ROOT, MEDIA_URL


class Application(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    title = models.CharField(verbose_name=_('title'), max_length=255, validators=[MinLengthValidator(4)],
                             help_text=_('Title for application at least 4 Char'))
    body = models.TextField(verbose_name=_('body'), help_text=_('You can use HTML tags to style your body.'))
    job_title = models.CharField(verbose_name=_('job title'), max_length=255)
    place_name = models.CharField(verbose_name=_('place name'), max_length=255, default=_('Not specified yet'))
    latitude = models.DecimalField(verbose_name=_('latitude'), max_digits=10, decimal_places=6, default=None, null=True,
                                   blank=True)
    longitude = models.DecimalField(verbose_name=_('longitude'), max_digits=10, decimal_places=6, default=None,
                                    null=True, blank=True)
    deadline = models.DateTimeField(verbose_name=_('deadline'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cover_pic = StdImageField(
        default='static/default/img/application.png',
        upload_to=UploadToPathAndRename('upload/img/application_cover'),
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


class Apply(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    english_skill = models.IntegerField(verbose_name=_('english skill'), choices=CRITERIA_CHOICES,
                                        blank=True, null=True)
    overall_skill = models.IntegerField(verbose_name=_('overall skill'), choices=CRITERIA_CHOICES,
                                        blank=True, null=True)
    leading_skill = models.IntegerField(verbose_name=_('leading skill'), choices=CRITERIA_CHOICES,
                                        blank=True, null=True)
    managing_skill = models.IntegerField(verbose_name=_('managing skill'), choices=CRITERIA_CHOICES,
                                         blank=True, null=True)
    communication_skill = models.IntegerField(verbose_name=_('communication skill'),
                                              choices=CRITERIA_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s took %s application by %s' % (self.user.worker.get_short_name(), self.application.title,
                                                 self.application.user.company.company_name)

    def is_all_filled(self):
        return all(map(
            lambda x: x[1] is not '' and x[1] is not None,
            self.__dict__.items()
        ))


class Question(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    question_text = models.CharField(verbose_name=_('question text'), max_length=200)
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
