from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

import re

SOCIAL_MEDIA_NAMES_REGEX = {
    'Facebook': r'''http(?:s)?:\/\/(?:www\.)?facebook\.com\/.*$''',
    'Twitter': r'''http(?:s)?:\/\/(?:www\.)?twitter\.com\/.*$''',
    'LinkedIn': r'''http(?:s)?:\/\/(?:www\.)?linkedin\.com\/in\/.*$''',
    'GitHub': r'''http(?:s)?:\/\/(?:www\.)?github\.com\/.*$'''
}


def social_url_checker(url):
    for key in SOCIAL_MEDIA_NAMES_REGEX.keys():
        if key.lower() in str(url).lower():
            expression = SOCIAL_MEDIA_NAMES_REGEX[key]
            if re.search(expression, str(url)):
                return url
            else:
                raise ValidationError(_('A invalid %s URL please double check' % key))
    return False

