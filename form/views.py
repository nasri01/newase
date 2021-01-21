import os
from ftplib import FTP
from statistics import mean, stdev

import jdatetime
import pytz
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from django.shortcuts import Http404, redirect, render
from django.template.loader import render_to_string
from weasyprint import CSS, HTML
from weasyprint.fonts import FontConfiguration

from acc.models import CalDevice, Licence, Record, UserProfile, AdTestType0
from report.models import Encode, Report
from ww.settings import STATICFILES_DIRS, STATIC_ROOT
from ww.local_settings import (DL_FTP_HOST, DL_FTP_PASSWD, DL_FTP_USER,
                               domain_name, DEBUG)

from acc.views import model_dict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@login_required
def router(request):
    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(
            name='employee') in request.user.groups.all():
        avatar_url = UserProfile.objects.get(
            id=1).avatar.url  # admin user_profile

        # return the Latest necessary form
        raw_test_form = model_dict[request.GET['test_form_type']][-1][1]
        # pop up a confirmation
        return render(request, 'acc/employee/index.html', {'form': raw_test_form, 'test_form_type': request.GET['test_form_type'],
                                                           'user_name': request.user.first_name,
                                                           'avatar_url': avatar_url})
    else:
        raise Http404


def delete_report(request):
    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(
            name='employee') in request.user.groups.all():

        model_name = request.GET['test_model_name'].split('_')
        model = model_dict[model_name[0]][int(model_name[1])]
        modelobj = model[0].objects.filter(
            record__number=int(request.GET['test_record_number']))

        modelobj[0].delete()
        modelobj = Report.objects.filter(
            record__number=int(request.GET['test_record_number']))
        if len(modelobj) == 1:
            modelobj[0].delete()

        return redirect('report_list', select_hospital=1)
    else:
        raise Http404


def save_router(request, formtype):
    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(
            name='employee') in request.user.groups.all():
        avatar_url = UserProfile.objects.get(
            id=1).avatar.url  # admin user_profile

        item = model_dict[formtype][-1]
        if request.POST['op_type'] == 'save':
            form1 = item[1](request.POST)

        elif request.POST['op_type'] == 'save_recal':
            # For backward compatibility for referencing
            for model in model_dict[formtype]:
                ref_data = model[0].objects.filter(
                    record__number=request.POST['test_ref_record_number'])
                if len(ref_data) == 1:
                    break

            form1 = item[1](request.POST)

        elif request.POST['op_type'] == 'save_edit':
            data = item[0].objects.all().get(
                record__number=request.POST['test_record_number'])
            form1 = item[1](request.POST, instance=data)

        elif request.POST['op_type'] == 'save_edit_recal':
            data = item[0].objects.all().get(
                record__number=request.POST['test_record_number'])
            # For backward compatibility for referencing
            for model in model_dict[formtype]:
                ref_data = model[0].objects.filter(Record=data.ref_record)
                if len(ref_data) == 1:
                    break
            form1 = item[1](request.POST, instance=data)
        else:
            form1 = item[1](request.POST)

        if form1.is_valid():
            sform = form1.save(commit=False)
            sform.user = request.user
            try:
                sform.date = jdatetime.datetime(
                    year=int(request.POST['report_year']),
                    month=int(request.POST['report_month']),
                    day=int(request.POST['report_day']),
                )
            except:
                sform.date = jdatetime.datetime.now().astimezone(pytz.timezone('Asia/Tehran'))

            sform.has_pdf = False

            if request.POST['op_type'] == 'save':
                sform.is_recal = False
                sform.ref_record = Record.objects.get(number=-1)
                record = Record.objects.create(
                    number=int(Record.objects.last().number) + 1)
                sform.record = record
                if formtype != 'CantTest':
                    sform.licence = Licence.objects.create(
                        number=int(Licence.objects.last().number) + 1)
                else:
                    ln = -1
                if (request.POST['status'] == '1'):
                    sform.is_done = True
                else:
                    sform.is_done = False
                green_status = f'اطلاعات {formtype} با موفقیت ذخیره شد! شماره گواهی'

            elif request.POST['op_type'] == 'save_edit':
                record = data.record
                sform.record = record
                ln = data.licence.number
                if request.POST['status'] == '1':
                    sform.is_done = True
                else:
                    sform.is_done = False
                green_status = f'اطلاعات با موفقیت ویرایش  شد! شماره گواهی'

            elif request.POST['op_type'] == 'save_recal':
                sform.is_recal = True
                sform.is_done = True  # always True
                record = Record.objects.create(
                    number=int(Record.objects.last().number) + 1)
                sform.record = record
                sform.ref_record = Record.objects.get(
                    number=request.POST['test_ref_record_number'])
                sform.licence = Licence.objects.create(
                    number=int(Licence.objects.last().number) + 1)
                if (request.POST['status'] == '1'):
                    ref_data.update(is_done=True)
                green_status = f'اطلاعات با موفقیت ذخیره شد! شماره گواهی ریکالیبراسیون'

            elif request.POST['op_type'] == 'save_edit_recal':
                record = data.record
                sform.record = record
                ln = data.licence.number
                if request.POST['status'] == '1':
                    ref_data.update(is_done=True)
                elif request.POST['status'] != '1':
                    ref_data.update(is_done=False)
                green_status = f'اطلاعات با موفقیت ویرایش شد! شماره گواهی ریکالیبراسیون:{ln}'
            else:
                green_status = f'اطلاعات با موفقیت ذخیره شد!'

            try:
                for i in range(1, 6):
                    setattr(sform, 'cal_dev_{}_cd'.format(i),
                            CalDevice.objects.get(id=request.POST['cal_dev{}'.format(i)]).calibration_date)
                    setattr(sform, 'cal_dev_{}_xd'.format(i),
                            CalDevice.objects.get(id=request.POST['cal_dev{}'.format(i)]).calibration_Expire_date)
            except:
                pass

            sform.save()
            # =====================================begin-Create PDF=========================
            # ===================================Begin-File Backing=================================================

            return render(request, 'acc/employee/index.html',
                          {'green_status': green_status, 'user_name': request.user.first_name,
                           'avatar_url': avatar_url, })
        else:  # form imcomplete
            return render(request, 'acc/employee/index.html',
                          {'form': form1, 'red_status': 'اطلاعات ناقص است!', 'form_type': item[0],
                           'user_name': request.user.first_name, 'avatar_url': avatar_url, })
    else:
        raise Http404


def reload(request, formtype):
    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(
            name='employee') in request.user.groups.all():
        avatar_url = UserProfile.objects.get(
            id=1).avatar.url  # admin user_profile
        form1 = model_dict[formtype][-1][1](request.POST)
        return render(request, 'acc/employee/index.html',
                      {'form': form1, 'test_form_type': item[0], 'user_name': request.user.first_name,
                               'avatar_url': avatar_url, 'reload': 1})
