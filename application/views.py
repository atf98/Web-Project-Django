from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from addon.decorators import language_scanner, company_required, worker_required
from application.models import Application, Apply, Question, Choice, QuestionTaker
from application.forms import ApplicationNewForm, QuestionAddForm, ApplyCompleteForm


@language_scanner
def index(request):
    context = {
        'applications': Application.objects.all()
    }
    if request.GET.get('q'):
        q = request.GET['q']
        opt = request.GET['search_option']
        context.update({
            'applications': search(request, q, request.GET['search_option']),
            'opt': opt,
            'q': q
        })
    context.update({'count': 0 if context['applications'] is None else context['applications'].count()})
    return render(request, 'application/index.html', context)


def search(r, q, obj):
    if obj == 'title':
        return Application.objects.filter(Q(title__contains=q))
    elif obj == 'month':
        try:
            q = int(q)
        except:
            pass
        if type(q) is str:
            messages.error(r, _('You can\'t use letters while searching for month!'))
            return
        return Application.objects.filter(Q(deadline__month=q))
    elif obj == 'job_title':
        return Application.objects.filter(Q(job_title__contains=q))
    elif obj == 'place':
        return Application.objects.filter(Q(place_name__contains=q))
    else:
        return Application.objects.filter(
            Q(title__contains=q) |
            Q(deadline__month=q) |
            Q(body__contains=q) |
            Q(job_title__contains=q) |
            Q(place_name__contains=q)
        )


@language_scanner
def application(request, id):
    application_info = Application.objects.get(pk=id)
    question = Question.objects.filter(application=application_info)
    if request.method == 'POST' and request.user.is_authenticated:
        if Apply.objects.filter(user=request.user, application=application_info).exists():
            messages.error(request, _('Sorry You have applied to this application, you can do it once!'))
        else:
            apply = Apply.objects.create(user=request.user, application=application_info)
            print(question)
            for ques in question:
                print(request.POST[str(ques.id)])
                temp = request.POST[str(ques.id)]
                if temp:
                    QuestionTaker.objects.create(question=ques, user=request.user, apply=apply, answer=temp)
    context = {
        'application': application_info,
        'question': question,
    }
    return render(request, 'application/single_application.html', context)


@login_required
@company_required
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


@login_required
@company_required
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


@login_required
@company_required
@language_scanner
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


@login_required
@company_required
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


@login_required
@company_required
@language_scanner
def complete_apply(request, id):
    apply = Apply.objects.get(pk=id)
    if request.method == 'POST':
        form = ApplyCompleteForm(request.POST)
        if form.is_valid():
            apply.overall_skill = request.POST['overall_skill']
            apply.managing_skill = request.POST['managing_skill']
            apply.leading_skill = request.POST['leading_skill']
            apply.communication_skill = request.POST['communication_skill']
            apply.english_skill = request.POST['english_skill']
            apply.save()
            return redirect('application:show_apply', id=apply.application.id)
    context = {
        'form': ApplyCompleteForm(instance=apply),
        'apply': apply
    }
    return render(request, 'application/complete_apply.html', context)


@login_required
@company_required(redirect_field_name='/application/')
@language_scanner
def delete(request, id):
    Application.objects.get(pk=id).delete()
    return redirect('application:home')
