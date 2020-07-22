# Generated by Django 3.0.8 on 2020-07-22 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0004_auto_20200722_1020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apply',
            name='communication_skill',
            field=models.IntegerField(blank=True, choices=[(1, 'High'), (2, 'Good'), (3, 'Medium'), (4, 'Low')], null=True, verbose_name='communication skill'),
        ),
        migrations.AlterField(
            model_name='apply',
            name='english_skill',
            field=models.IntegerField(blank=True, choices=[(1, 'High'), (2, 'Good'), (3, 'Medium'), (4, 'Low')], null=True, verbose_name='english skill'),
        ),
        migrations.AlterField(
            model_name='apply',
            name='leading_skill',
            field=models.IntegerField(blank=True, choices=[(1, 'High'), (2, 'Good'), (3, 'Medium'), (4, 'Low')], null=True, verbose_name='leading skill'),
        ),
        migrations.AlterField(
            model_name='apply',
            name='managing_skill',
            field=models.IntegerField(blank=True, choices=[(1, 'High'), (2, 'Good'), (3, 'Medium'), (4, 'Low')], null=True, verbose_name='managing skill'),
        ),
        migrations.AlterField(
            model_name='apply',
            name='overall_skill',
            field=models.IntegerField(blank=True, choices=[(1, 'High'), (2, 'Good'), (3, 'Medium'), (4, 'Low')], null=True, verbose_name='overall skill'),
        ),
    ]
