from django.apps import apps

from celery import shared_task

from stdimage.utils import render_variations


@shared_task
def process_photo_image(file_name, variations, storage):
    render_variations(file_name, variations, replace=True, storage=storage)
    obj = apps.get_model('account', 'Account').objects.get(profile_pic=file_name)
    obj.processed = True
    obj.save()
