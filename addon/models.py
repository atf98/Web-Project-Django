from django.db import models
from addon.models_addon import LANGUAGE_CHOICES
from django.utils.translation import ugettext_lazy as _


class GlobalSetting(models.Model):
    token = models.CharField(max_length=255)
    language = models.CharField(default='en-us', choices=LANGUAGE_CHOICES, max_length=5)

    def __str__(self):
        return self.token

    class Meta:
        verbose_name = _('global setting')
        verbose_name_plural = _('global setting')
