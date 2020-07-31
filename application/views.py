from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from addon.decorators import language_scanner, company_required, worker_required
from application.models import (
    Application, Apply, Question, Choice, QuestionTaker, ApplicationImage, ApplicationFile
)
from application.forms import (
    ApplicationNewForm, QuestionAddForm, ApplyCompleteForm, ApplicationImageForm, ApplicationFileForm
)


@language_scanner
def index(request):
    context = {
        'applications': Application.objects.all()
    }
    if request.GET.get('q'):
        q = request.GET['q']
        if request.GET.get('search_option'):
            opt = request.GET['search_option']
        else:
            opt = 'title'
        context.update({
            'applications': search(request, q, opt),
            'opt': opt,
            'q': q
        })

    context.update({'count': 0 if context['applications'] is None else context['applications'].count()})
    if request.GET.get('view'):
        view = request.GET['view']
        return render(request, 'application/index_%s.html' % view, context)
    else:
        return render(request, 'application/index_grid.html', context)


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
            Q(body__contains=q) |
            Q(job_title__contains=q) |
            Q(place_name__contains=q)
        )


@language_scanner
def application(request, id):
    application_info = Application.objects.get(pk=id)
    question = Question.objects.filter(application=application_info)
    images = ApplicationImage.objects.filter(application=application_info)
    if request.method == 'POST' and request.user.is_authenticated:
        if Apply.objects.filter(user=request.user, application=application_info).exists():
            messages.error(request, _('Sorry You have applied to this application, you can do it once!'))
        else:
            apply = Apply.objects.create(user=request.user, application=application_info)
            for ques in question:
                if request.POST[str(ques.id)]:
                    QuestionTaker.objects.create(question=ques, user=request.user, apply=apply, answer=request.POST[
                        str(ques.id)])
            messages.success(request, _('We have placed your apply, will notify you when company review it.'))
    context = {
        'application': application_info,
        'images': images,
        'question': question,
        'exists': Apply.objects.filter(application=application_info, user=request.user).exists()
    }
    return render(request, 'application/application_details.html', context)


@login_required
@company_required
@language_scanner
def new(request):
    context = {
        'form': ApplicationNewForm(),
        'form_image': ApplicationImageForm(),
        'form_file': ApplicationFileForm(),
    }
    if request.method == 'POST':
        form = ApplicationNewForm(request.POST)
        form_image = ApplicationImageForm(request.POST, request.FILES or None)
        form_file = ApplicationImageForm(request.POST, request.FILES or None)
        if request.user.is_company:
            if form.is_valid() and form_image.is_valid() and form_file.is_valid():
                application_form = form.save(commit=False)
                application_form.user = request.user
                application_form.save()
                if request.FILES.getlist('file'):
                    for file in request.FILES.getlist('file'):
                        ApplicationFile.objects.create(application=application_form, file=file, real_name=file.name)
                if request.FILES.getlist('image'):
                    if request.FILES.getlist('image').count() == 0:
                        ApplicationImage.objects.create(application=application_form, real_name=application_form.title)
                    for image in request.FILES.getlist('image'):
                        ApplicationImage.objects.create(application=application_form, image=image, real_name=image.name)
                return redirect('application:detail', id=application_form.id)
            else:
                messages.error(request, _('Sorry something went wrong, please try again!'))
        else:
            messages.error(request, _('You are not Company so you can add Application'))
        context.update({'form': form})
    return render(request, 'application/application_new.html', context)


@login_required
@company_required
@language_scanner
def add_question(request, id):
    application_info = get_object_or_404(Application, pk=id)
    if request.user == application_info.user:
        if request.method == 'POST':
            form = QuestionAddForm(request.POST)

            if form.is_valid():
                question = form.save(commit=False)
                question.application = application_info
                question.save()
                if not all(choice is '' for choice in request.POST.getlist('choice')):
                    for choice in request.POST.getlist('choice'):
                        Choice.objects.create(question=question, choice_text=choice)

                messages.success(request, _('Question Added!'))
        context = {
            'application': application_info,
            'form': QuestionAddForm()
        }
        return render(request, 'application/question_add.html', context)
    else:
        messages.error(request, _('Not your application!'))
        return redirect('application:home')


@login_required
@company_required
@language_scanner
def edit(request, id):
    application_info = Application.objects.get(pk=id)
    if request.user == application_info.user:
        context = {
            'application': application_info,
            'form': ApplicationNewForm(instance=application_info)
        }

        if request.method == 'POST':
            _app = ApplicationNewForm(request.POST or None, request.FILES or None, instance=application_info)
            if _app.is_valid():
                _app.save()
                messages.success(request, _('Application Updated'))
            context.update({'form': _app})
        return render(request, 'application/application_edit.html', context)
    else:
        messages.error(request, _('Not your application!'))
        return redirect('application:home')


@login_required
@company_required
@language_scanner
def show_apply(request, id):
    application_info = Application.objects.get(pk=id)
    if request.user == application_info.user:
        applies = Apply.objects.filter(application=application_info)
        takers = QuestionTaker.objects.filter(apply__in=applies)

        context = {
            'application': application_info,
            'applies': applies,
            'takers': takers,
        }
        return render(request, 'application/applies_show.html', context)
    else:
        messages.error(request, _('Not your application!'))
        return redirect('application:home')


@login_required
@company_required
@language_scanner
def complete_apply(request, id):
    apply = Apply.objects.get(pk=id)
    if request.user == apply.application.user:
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
        return render(request, 'application/applies_complete.html', context)
    else:
        messages.error(request, _('Not your application!'))
        return redirect('application:home')


@login_required
@company_required(redirect_field_name='/application/')
@language_scanner
def delete(request, id):
    application_info = Application.objects.get(pk=id)
    if request.user == application_info.user:
        application_info.delete()
        return redirect('application:home')
    else:
        messages.error(request, _('Not your application!'))
        return redirect('application:home')
