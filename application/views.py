from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from addon.decorators import language_scanner
from application.models import Application, Apply, Question, Choice, QuestionTaker
from application.forms import ApplicationNewForm, QuestionAddForm, ApplyCompleteForm


@language_scanner
def index(request):
    context = {
        'applications': Application.objects.all()
    }
    return render(request, 'application/index.html', context)


@language_scanner
def application(request, id):
    context = {
        'application': Application.objects.get(pk=id)
    }
    return render(request, 'application/single_application.html', context)


@language_scanner
def new(request):
    context = {
        'form': ApplicationNewForm()
    }
    if request.method == 'POST':
        form = ApplicationNewForm(request.POST, request.FILES or None)
        if request.user.is_company:
            if form.is_valid():
                application_form = form.save(commit=False)
                application_form.user = request.user
                application_form.cover_pic = request.FILES['cover_pic']
                application_form.save()
                return redirect('application:detail', id=application_form.id)
            messages.error(request, _('Sorry something went wrong, please try again!'))
        messages.error(request, _('You can\'t add application'))
        context.update({'form': form})
    return render(request, 'application/new.html', context)


@language_scanner
def add_question(request, id):
    app_info = get_object_or_404(Application, pk=id)
    if request.method == 'POST':
        form = QuestionAddForm(request.POST)

        if form.is_valid():
            question = form.save(commit=False)
            question.application = app_info
            question.save()
            if request.POST['question_type'] == 'TextAn':
                Choice.objects.create(question=question, choice_text=request.POST['text_answer'])
            else:
                for choice in request.POST.getlist('choice'):
                    Choice.objects.create(question=question, choice_text=choice)

            messages.success(request, 'Question Added!')
    context = {
        'application': app_info,
        'form': QuestionAddForm()
    }
    return render(request, 'application/add_question.html', context)


def edit(request, id):
    application_info = Application.objects.get(pk=id)
    if request.method == 'POST':
        _app = ApplicationNewForm(request.POST, instance=application_info)
        _app.save()
        messages.success(request, 'Application Updated')
    context = {
        'application': application_info,
        'form': ApplicationNewForm(instance=application_info)
    }
    return render(request, 'application/edit.html', context)


@language_scanner
def show_apply(request, id):
    application_info = Application.objects.get(pk=id)
    applies = Apply.objects.filter(application=application_info)
    takers = QuestionTaker.objects.filter(apply__in=applies)

    context = {
        'application': application_info,
        'applies': applies,
        'takers': takers,
    }
    return render(request, 'application/show_applies.html', context)


@language_scanner
def complete_apply(request, id):
    apply = Apply.objects.get(pk=id)
    context = {
        'form': ApplyCompleteForm(instance=apply),
        'apply': apply
    }
    return render(request, 'application/complete_apply.html', context)


def delete(request, id):
    Application.objects.get(pk=id).delete()
    return redirect('application:home')
