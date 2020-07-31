from django.template.defaultfilters import stringfilter
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

from application.models_addon import CRITERIA_CHOICES

import re


register = template.Library()


@register.filter
def choices(number):
    return mark_safe(CRITERIA_CHOICES[int(number)-1][1])


@register.filter
@stringfilter
def upto(value, delimiter=None):
    return value.split(delimiter)[0]


@register.filter
def readmore(txt, show_words=15):
    words = re.split(r' ', escape(txt))

    if len(words) <= show_words:
        return txt

    return mark_safe(' '.join(words))


choices.is_safe = True
upto.is_safe = True
readmore.is_safe = True
