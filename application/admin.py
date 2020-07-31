from django.contrib import admin
from application.models import Application, Apply, Question, Choice, QuestionTaker, ApplicationImage, ApplicationFile


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'job_title', 'deadline', 'created_at', 'updated_at',)
    search_fields = ('title', 'job_title')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class ApplyAdmin(admin.ModelAdmin):
    list_display = ('user', 'application', 'created_at', 'updated_at',)
    search_fields = ()
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'created_at', 'updated_at',)
    search_fields = ('question_text',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class QuestionTakerAdmin(admin.ModelAdmin):
    list_display = ('question', 'user', 'apply', 'updated_at',)
    search_fields = ()
    readonly_fields = ('updated_at', )
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'choice_text')
    search_fields = ()
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Application, ApplicationAdmin)
admin.site.register(Apply, ApplyAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(QuestionTaker, QuestionTakerAdmin)
admin.site.register(ApplicationFile)
admin.site.register(ApplicationImage)
