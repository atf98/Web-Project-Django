from django import forms
from django.utils.translation import ugettext_lazy as _

from application.models_addon import CRITERIA_CHOICES
from application.models import Application, Apply, Question, Choice, ApplicationImage, ApplicationFile
from datetime import datetime


class ApplicationNewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'autofocus': 'autofocus'}
        )
        self.fields['body'].widget = forms.Textarea(
            attrs={'class': 'form-control', 'id': 'BodyInput', }
        )
        self.fields['job_title'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'data_column': '6', 'first': 'true', }
        )
        self.fields['place_name'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'data_column': '6', 'last': 'true', }
        )
        self.fields['latitude'].widget = forms.NumberInput(
            attrs={'class': 'form-control', 'data_column': '6', 'pattern': "[0-9]+([,][0-9]{1,2})?", 'first': 'true',
                   'step': "0.000000000000000001", 'lang': 'en'}
        )
        self.fields['longitude'].widget = forms.NumberInput(
            attrs={'class': 'form-control', 'data_column': '6', 'pattern': "[0-9]+([,][0-9]{1,2})?", 'last': 'true',
                   'step': "0.000000000000000001", 'lang': 'en'}
        )
        self.fields['deadline'].widget = forms.DateTimeInput(
            attrs={'class': 'form-control datepicker', 'type': 'date', }
        )

    class Meta:
        model = Application
        fields = ['title', 'body', 'job_title', 'place_name', 'deadline', 'latitude', 'longitude']

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if datetime.strptime(str(deadline)[:19], '%Y-%m-%d %H:%M:%S') < datetime.today():
            raise forms.ValidationError(_('Deadline cannot be in past!'))
        return deadline


class ApplicationImageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget = forms.FileInput(
            attrs={'class': 'form-control', 'multiple': ''}
        )
        self.fields['image'].required = False

    class Meta:
        model = ApplicationImage
        fields = ['image']


class ApplicationFileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget = forms.FileInput(
            attrs={'class': 'form-control wrapper js', 'multiple': ''}
        )
        self.fields['file'].required = False

    class Meta:
        model = ApplicationFile
        fields = ['file']


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
