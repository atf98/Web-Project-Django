from django import forms
from django.utils.translation import ugettext_lazy as _

from application.models_addon import CRITERIA_CHOICES
from application.models import Application, Apply, Question, Choice

LINK = 'https://support.google.com/maps/answer/18539?co=GENIE.Platform%3DDesktop&hl=en#6387158'


class ApplicationNewForm(forms.ModelForm):
    title = forms.CharField(label=_('Title'), required=True,
                            widget=forms.TextInput(attrs={
                                'id': 'TitleInput',
                                'class': 'form-control',
                                'placeholder': _('Title'),
                                'autofocus': 'autofocus',
                            }),
                            error_messages={
                                'required': _('Make Sure to fill this input.')
                            })
    body = forms.CharField(label=_('Body'), required=True,
                           widget=forms.Textarea(attrs={
                               'id': 'BodyInput',
                               'class': 'form-control',
                               'placeholder': _('Body'),
                           }),
                           error_messages={
                               'required': _('Make Sure to fill this input.')
                           })
    job_title = forms.CharField(label=_('Job Title'), required=True,
                                widget=forms.TextInput(attrs={
                                    'id': 'JobTitleInput',
                                    'class': 'form-control',
                                    'placeholder': _('Job Title'),
                                    'data_column': '6',
                                    'first': 'true'
                                }),
                                error_messages={
                                    'required': _('Make Sure to fill this input.')
                                })
    place_name = forms.CharField(label=_('Place Name'), required=True,
                                 widget=forms.TextInput(attrs={
                                     'id': 'PlaceNameInput',
                                     'class': 'form-control',
                                     'placeholder': _('Place Name'),
                                     'data_column': '6',
                                     'last': 'true'
                                 }),
                                 error_messages={
                                     'required': _('Make Sure to fill this input.')
                                 })
    latitude = forms.DecimalField(label=_('Latitude'), required=False,
                                  widget=forms.TextInput(attrs={
                                      'id': 'LatitudeInput',
                                      'class': 'form-control',
                                      'placeholder': _('Latitude'),
                                      'data_column': '6',
                                      'first': 'true'
                                  }))
    longitude = forms.DecimalField(label=_('Longitude'), required=False,
                                   widget=forms.TextInput(attrs={
                                       'id': 'LongitudeInput',
                                       'class': 'form-control',
                                       'placeholder': _('Longitude'),
                                       'data_column': '6',
                                       'last': 'true'
                                   }),
                                   help_text=_(
                                       'Make sure to put the right coordinates (follow this <a href="%s">link</a>)' % LINK))
    deadline = forms.DateTimeField(label=_('Deadline'), required=True,
                                   help_text=_('Note that the end time will be at the midnight of the day you picked.'),
                                   widget=forms.DateTimeInput(attrs={
                                       'id': 'DeadlineInput',
                                       'class': 'form-control datepicker',
                                       'type': 'date',
                                   }))
    cover_pic = forms.ImageField(label=_('Application Cover'),
                                 widget=forms.FileInput(attrs={
                                     'id': 'ApplicationCoverInput',
                                     'class': 'form-control',
                                 }))

    class Meta:
        model = Application
        fields = ['title', 'cover_pic', 'body', 'job_title', 'place_name', 'latitude', 'longitude', 'deadline']


class QuestionAddForm(forms.ModelForm):
    question_text = forms.CharField(label=_('Question Text'), required=True,
                                    widget=forms.TextInput(attrs={
                                        'id': 'QuestionTextInput',
                                        'class': 'form-control',
                                        'placeholder': _('Question Text'),
                                    }),
                                    error_messages={
                                        'required': _('Make Sure to fill this input.')
                                    })

    class Meta:
        model = Question
        fields = ['question_text']


class ApplyCompleteForm(forms.ModelForm):
    overall_skill = forms.IntegerField(label=_('Overall Skill'), required=True,
                                       widget=forms.Select(attrs={
                                           'id': 'QuestionTextInput',
                                           'class': 'form-control',
                                           'placeholder': _('Question Text'),
                                       }, choices=CRITERIA_CHOICES),
                                       error_messages={
                                           'required': _('Make Sure to fill this input.')
                                       })
    managing_skill = forms.IntegerField(label=_('Managing Skill'), required=True,
                                        widget=forms.Select(attrs={
                                            'id': 'QuestionTextInput',
                                            'class': 'form-control',
                                            'placeholder': _('Question Text'),
                                        }, choices=CRITERIA_CHOICES),
                                        error_messages={
                                            'required': _('Make Sure to fill this input.')
                                        })
    leading_skill = forms.IntegerField(label=_('Leading Skill'), required=True,
                                       widget=forms.Select(attrs={
                                           'id': 'QuestionTextInput',
                                           'class': 'form-control',
                                           'placeholder': _('Question Text'),
                                       }, choices=CRITERIA_CHOICES),
                                       error_messages={
                                           'required': _('Make Sure to fill this input.')
                                       })
    communication_skill = forms.IntegerField(label=_('Communication Skill'), required=True,
                                             widget=forms.Select(attrs={
                                                 'id': 'QuestionTextInput',
                                                 'class': 'form-control',
                                                 'placeholder': _('Question Text'),
                                             }, choices=CRITERIA_CHOICES),
                                             error_messages={
                                                 'required': _('Make Sure to fill this input.')
                                             })
    english_skill = forms.IntegerField(label=_('English Skill'), required=True,
                                       widget=forms.Select(attrs={
                                           'id': 'QuestionTextInput',
                                           'class': 'form-control',
                                           'placeholder': _('Question Text'),
                                       }, choices=CRITERIA_CHOICES),
                                       error_messages={
                                           'required': _('Make Sure to fill this input.')
                                       })

    class Meta:
        model = Apply
        fields = ['overall_skill', 'managing_skill', 'leading_skill', 'communication_skill', 'english_skill']

