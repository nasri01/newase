# Generated by Django 3.0.7 on 2020-06-28 06:44

from django.db import migrations
import django_jalali.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('acc', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='date',
            field=django_jalali.db.models.jDateField(auto_now_add=True, verbose_name='تاریخ میلادی دستگاه'),
        ),
    ]
