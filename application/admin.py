from django.contrib import admin
from application.models import Application, Apply, Question, Choice, QuestionTaker

admin.site.register(Application)
admin.site.register(Apply)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(QuestionTaker)
