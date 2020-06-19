import hashlib
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
from ww.settings import STATICFILES_DIRS ,STATIC_ROOT
from ww.local_settings import (DL_FTP_HOST, DL_FTP_PASSWD, DL_FTP_USER,
                               domain_name, DEBUG)


from .forms import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model_list = [['MonitorSpo2', MonitorSpo2_1, MonitorSpo2_1_Form, 3],
              ['MonitorECG', MonitorECG_1, MonitorECG_1_Form, 3],
              ['MonitorNIBP', MonitorNIBP_1, MonitorNIBP_1_Form, 3],
              ['MonitorSafety', MonitorSafety_1, MonitorSafety_1_Form, 3],
              ['AED', AED_1, AED_1_Form, 2],
              ['AnesthesiaMachine', AnesthesiaMachine_1,
               AnesthesiaMachine_1_Form, 4],
              ['Defibrilator', Defibrilator_1, Defibrilator_1_Form, 4],
              ['ECG', ECG_1, ECG_1_Form, 4],
              ['FlowMeter', FlowMeter_1, FlowMeter_1_Form, 1],
              ['InfusionPump', InfusionPump_1, InfusionPump_1_Form, 4],
              ['ManoMeter', ManoMeter_1, ManoMeter_1_Form, 3],
              ['spo2', Spo2_1, spo2_1_Form, 4],
              ['Suction', Suction_1, suction_1_Form, 4],
              ['SyringePump', SyringePump_1, syringe_pump_1_Form, 4],
              ['Ventilator', Ventilator_1, ventilator_1_Form, 4],
              ['ElectroCauter', ElectroCauter_1, electrocauter_1_Form, 5],
              ['CantTest', CantTest, CantTest_Form, 0],
              ]


@login_required
def router(request):

    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(name='employee') in request.user.groups.all():
        avatar_url = UserProfile.objects.get(
            id=1).avatar.url  # admin user_profile
        for item in model_list:
            if request.GET['type'] == item[0]:
                form1 = item[2]
                # pop up a confirmation
                return render(request, 'acc/employee/index.html', {'form': form1, 'form_type': item[0],
                                                                   'user_name': request.user.first_name, 'avatar_url': avatar_url})
    else:
        raise Http404


def delete_report(request):
    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(name='employee') in request.user.groups.all():
        for model in model_list:
            modelobj = model[1].objects.filter(
                record__number=int(request.GET['record_number']))
            if len(modelobj) == 1:
                modelobj[0].delete()
                modelobj = Report.objects.filter(
                    record__number=int(request.GET['record_number']))
                modelobj[0].delete()
                break

        return redirect('report_list')
    else:
        raise Http404


def send_file_ftp(ftp_obj, filename, report_name):
    fp = open(report_name, 'rb')
    ftp_obj.storbinary('STOR %s' % os.path.basename(filename), fp, 8192)


def save_router(request, formtype):
    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(name='employee') in request.user.groups.all():
        avatar_url = UserProfile.objects.get(
            id=1).avatar.url  # admin user_profile
        for item in model_list:
            if formtype == item[0]:

                if request.POST['op_type'] == 'save':
                    form1 = item[2](request.POST)

                elif request.POST['op_type'] == 'save_recal':
                    ref_data = item[1].objects.get(
                        record__number=request.POST['ref_record_number'])
                    form1 = item[2](request.POST)

                elif request.POST['op_type'] == 'save_edit':
                    data = item[1].objects.all().get(
                        record__number=request.POST['record_number'])
                    form1 = item[2](request.POST, instance=data)

                elif request.POST['op_type'] == 'save_edit_recal':
                    data = item[1].objects.all().get(
                        record__number=request.POST['record_number'])
                    ref_data = item[1].objects.get(Record=data.ref_record)
                    form1 = item[2](request.POST, instance=data)
                else:
                    form1 = item[2](request.POST)

                if form1.is_valid():
                    sform = form1.save(commit=False)
                    sform.user = request.user
                    sform.date = jdatetime.datetime.now().astimezone(pytz.timezone('Asia/Tehran'))
                    sform.has_pdf = False

                    if request.POST['op_type'] == 'save':
                        sform.is_recal = False
                        sform.ref_record = Record.objects.get(number=-1)
                        record = Record.objects.create(
                            number=int(Record.objects.last().number)+1)
                        sform.record = record
                        if item[0] != 'CantTest':
                            ln = int(Licence.objects.order_by('number')[
                                len(Licence.objects.all())-1].number) + 1
                            sform.licence = Licence.objects.create(number=ln)
                        else:
                            ln = -1
                        if (request.POST['status'] == '1'):
                            sform.is_done = True
                        else:
                            sform.is_done = False
                        green_status = f'اطلاعات {item[0]} با موفقیت ذخیره شد! شماره گواهی:{ln}'

                    elif request.POST['op_type'] == 'save_edit':
                        record = data.record
                        sform.record = record
                        ln = data.licence.number
                        if (request.POST['status'] == '1'):
                            sform.is_done = True
                        else:
                            sform.is_done = False
                        green_status = f'اطلاعات با موفقیت ویرایش  شد! شماره گواهی:{ln}'

                    elif request.POST['op_type'] == 'save_recal':
                        sform.is_recal = True
                        sform.is_done = True  # always True
                        record = Record.objects.create(
                            number=int(Record.objects.last().number)+1)
                        sform.record = record
                        sform.ref_record = Record.objects.get(
                            number=request.POST['ref_record_number'])
                        ln = int(Licence.objects.order_by('number')[
                                 len(Licence.objects.all()) - 1].number) + 1
                        sform.licence = Licence.objects.create(number=ln)
                        if (request.POST['status'] == '1'):
                            ref_data.is_done = True
                            ref_data.save()
                        green_status = f'اطلاعات با موفقیت ذخیره شد! شماره گواهی ریکالیبراسیون:{ln}'

                    elif request.POST['op_type'] == 'save_edit_recal':
                        record = data.record
                        sform.record = record
                        ln = data.licence.number
                        if (request.POST['status'] == '1'):
                            ref_data.is_done = True
                        elif request.POST['status'] != '1':
                            ref_data.is_done = False
                        ref_data.save()
                        green_status = f'اطلاعات با موفقیت ویرایش شد! شماره گواهی ریکالیبراسیون:{ln}'
                    else:
                        green_status = f'اطلاعات با موفقیت ذخیره شد!'

                    if (item[3] != 0):
                        sform.cal_dev_1_cd = CalDevice.objects.get(
                            id=request.POST['cal_dev1']).calibration_date
                        sform.cal_dev_1_xd = CalDevice.objects.get(
                            id=request.POST['cal_dev1']).calibration_Expire_date
                        if (item[3] >= 2):
                            sform.cal_dev_2_cd = CalDevice.objects.get(
                                id=request.POST['cal_dev2']).calibration_date
                            sform.cal_dev_2_xd = CalDevice.objects.get(
                                id=request.POST['cal_dev2']).calibration_Expire_date
                            if (item[3] >= 3):
                                sform.cal_dev_3_cd = CalDevice.objects.get(
                                    id=request.POST['cal_dev3']).calibration_date
                                sform.cal_dev_3_xd = CalDevice.objects.get(
                                    id=request.POST['cal_dev3']).calibration_Expire_date
                                if (item[3] >= 4):
                                    sform.cal_dev_4_cd = CalDevice.objects.get(
                                        id=request.POST['cal_dev4']).calibration_date
                                    sform.cal_dev_4_xd = CalDevice.objects.get(
                                        id=request.POST['cal_dev4']).calibration_Expire_date
                                    if (item[3] == 5):
                                        sform.cal_dev_5_cd = CalDevice.objects.get(
                                            id=request.POST['cal_dev5']).calibration_date
                                        sform.cal_dev_5_xd = CalDevice.objects.get(
                                            id=request.POST['cal_dev5']).calibration_Expire_date
                    sform.save()
                    # =====================================begin-Create PDF=========================
                    # ===================================Begin-File Backing=================================================
                    data = []
                    if(item[1] == MonitorSpo2_1):
                        template_name = 'report/Monitor/Spo2/licence1.html'
                        ss = 0
                        sss = 0
                        data.append((int(sform.s2_e1_spo2) - 70)**2)  # 0
                        data.append((int(sform.s2_e2_spo2) - 75)**2)  # 1
                        data.append((int(sform.s2_e3_spo2) - 80)**2)  # 2
                        data.append((int(sform.s2_e4_spo2) - 85)**2)  # 3
                        data.append((int(sform.s2_e5_spo2) - 88)**2)  # 4
                        data.append((int(sform.s2_e6_spo2) - 90)**2)  # 5
                        data.append((int(sform.s2_e7_spo2) - 92)**2)  # 6
                        data.append((int(sform.s2_e8_spo2) - 94)**2)  # 7
                        data.append((int(sform.s2_e9_spo2) - 96)**2)  # 8
                        data.append((int(sform.s2_e10_spo2) - 98)**2)  # 9
                        data.append((int(sform.s2_e11_spo2) - 100)**2)  # 10
                        for i in range(11):
                            ss += data[i]
                        data.append(int(((ss/11)**0.5)*100)/100)  # 11

                        data.append((int(sform.s3_e1_pr) - 35)**2)  # 12
                        data.append((int(sform.s3_e2_pr) - 60)**2)  # 13
                        data.append((int(sform.s3_e3_pr) - 100)**2)  # 14
                        data.append((int(sform.s3_e4_pr) - 200)**2)  # 15
                        data.append((int(sform.s3_e5_pr) - 240)**2)  # 16
                        for i in range(12, 17):
                            sss += data[i]
                        data.append(int(((sss/5)**0.5)*100)/100)  # 17

                    elif item[1] == MonitorNIBP_1:
                        template_name = 'report/Monitor/NIBP/licence1.html'
                        data1 = []
                        data2 = []
                        data3 = []

                        data3.append(
                            0 if abs(int(sform.s1_e1_simp) - int(sform.s1_e1_nibpp)) >= max(3, int(sform.s1_e1_simp) * 0.03) else 1 )
                        data3.append(
                            0 if abs(int(sform.s1_e1_simp) - int(sform.s1_e1_nibpp)) >= max(3, int(sform.s1_e1_simp) * 0.03) else 1 )
                        data3.append(
                            0 if abs(int(sform.s1_e1_simp) - int(sform.s1_e1_nibpp)) >= max(3, int(sform.s1_e1_simp) * 0.03) else 1 )
                        data3.append(
                            0 if abs(int(sform.s1_e1_simp) - int(sform.s1_e1_nibpp)) >= max(3, int(sform.s1_e1_simp) * 0.03) else 1 )
                        data3.append(
                            0 if abs(int(sform.s1_e1_simp) - int(sform.s1_e1_nibpp)) >= max(3, int(sform.s1_e1_simp) * 0.03) else 1 )
                        data3.append(
                            0 if abs(int(sform.s1_e1_simp) - int(sform.s1_e1_nibpp)) >= max(3, int(sform.s1_e1_simp) * 0.03) else 1 )
                        data3.append(
                            0 if abs(int(sform.s1_e1_simp) - int(sform.s1_e1_nibpp)) >= max(3, int(sform.s1_e1_simp) * 0.03) else 1 )
                        data3.append(
                            0 if abs(int(sform.s1_e1_simp) - int(sform.s1_e1_nibpp)) >= max(3, int(sform.s1_e1_simp) * 0.03) else 1 )
                            

                        data1.append(int(sform.s2_e1_pr1.split('/')[0]))
                        data1.append(int(sform.s2_e1_pr2.split('/')[0]))
                        data1.append(int(sform.s2_e1_pr3.split('/')[0]))
                        data1.append(int(sform.s2_e2_pr1.split('/')[0]))
                        data1.append(int(sform.s2_e2_pr2.split('/')[0]))
                        data1.append(int(sform.s2_e2_pr3.split('/')[0]))
                        data1.append(int(sform.s2_e3_pr1.split('/')[0]))
                        data1.append(int(sform.s2_e3_pr2.split('/')[0]))
                        data1.append(int(sform.s2_e3_pr3.split('/')[0]))
                        data1.append(int(sform.s2_e4_pr1.split('/')[0]))
                        data1.append(int(sform.s2_e4_pr2.split('/')[0]))
                        data1.append(int(sform.s2_e4_pr3.split('/')[0]))
                        data1.append(int(sform.s2_e5_pr1.split('/')[0]))
                        data1.append(int(sform.s2_e5_pr2.split('/')[0]))
                        data1.append(int(sform.s2_e5_pr3.split('/')[0]))
                        data1.append(int(sform.s2_e6_pr1.split('/')[0]))
                        data1.append(int(sform.s2_e6_pr2.split('/')[0]))
                        data1.append(int(sform.s2_e6_pr3.split('/')[0]))
                        data2.append(int(sform.s2_e1_pr1.split('/')[1]))
                        data2.append(int(sform.s2_e1_pr2.split('/')[1]))
                        data2.append(int(sform.s2_e1_pr3.split('/')[1]))
                        data2.append(int(sform.s2_e2_pr1.split('/')[1]))
                        data2.append(int(sform.s2_e2_pr2.split('/')[1]))
                        data2.append(int(sform.s2_e2_pr3.split('/')[1]))
                        data2.append(int(sform.s2_e3_pr1.split('/')[1]))
                        data2.append(int(sform.s2_e3_pr2.split('/')[1]))
                        data2.append(int(sform.s2_e3_pr3.split('/')[1]))
                        data2.append(int(sform.s2_e4_pr1.split('/')[1]))
                        data2.append(int(sform.s2_e4_pr2.split('/')[1]))
                        data2.append(int(sform.s2_e4_pr3.split('/')[1]))
                        data2.append(int(sform.s2_e5_pr1.split('/')[1]))
                        data2.append(int(sform.s2_e5_pr2.split('/')[1]))
                        data2.append(int(sform.s2_e5_pr3.split('/')[1]))
                        data2.append(int(sform.s2_e6_pr1.split('/')[1]))
                        data2.append(int(sform.s2_e6_pr2.split('/')[1]))
                        data2.append(int(sform.s2_e6_pr3.split('/')[1]))

                        for id in range(3):
                            data1[id] = abs(data1[id] - 60)
                            data2[id] = abs(data2[id] - 30)
                        for id in range(3, 6):
                            data1[id] = abs(data1[id] - 80)
                            data2[id] = abs(data2[id] - 50)
                        for id in range(6, 9):
                            data1[id] = abs(data1[id] - 120)
                            data2[id] = abs(data2[id] - 80)
                        for id in range(9, 12):
                            data1[id] = abs(data1[id] - 200)
                            data2[id] = abs(data2[id] - 150)
                        for id in range(12, 15):
                            data1[id] = abs(data1[id] - 35)
                            data2[id] = abs(data2[id] - 15)
                        for id in range(15, 18):
                            data1[id] = abs(data1[id] - 100)
                            data2[id] = abs(data2[id] - 70)

                        print(data1)
                        print(data2)
                        data.append(sum(data1))  # 0
                        data.append(sum(data2))  # 1
                        data.append(round(mean(data1), 2))  # 2
                        data.append(round(mean(data2), 2))  # 3
                        data.append(round(stdev(data1), 2))  # 4
                        data.append(round(stdev(data2), 2))  # 5
                        data.append(data3)  # 6

                        data.append(data1)  # 7
                        data.append(data2)  # 8

                    elif (item[1] == MonitorECG_1):
                        template_name = 'report/Monitor/ECG/licence1.html'

                    elif (item[1] == MonitorSafety_1):
                        template_name = 'report/Monitor/SAFETY/licence1.html'

                    elif (item[1] == AED_1):
                        template_name = 'report/AED/licence1.html'

                    elif (item[1] == AnesthesiaMachine_1):
                        template_name = 'report/AnesthesiaMachine/licence1.html'

                    elif (item[1] == Defibrilator_1):
                        template_name = 'report/Defibrilator/licence1.html'

                        diff = abs(sform.s7a_e1_se - sform.s7a_e1_es)
                        data.append(max(diff, 0.15 * sform.s7a_e1_se))  # 0
                        diff = abs(sform.s7a_e2_se - sform.s7a_e2_es)
                        data.append(max(diff, 0.15 * sform.s7a_e2_se))  # 1
                        diff = abs(sform.s7a_e3_se - sform.s7a_e3_es)
                        data.append(max(diff, 0.15 * sform.s7a_e3_se))  # 2

                        diff = abs(sform.s7c_e1_se - sform.s7c_e1_es)
                        data.append(max(diff, 0.15 * sform.s7c_e1_se))  # 3
                        diff = abs(sform.s7c_e2_se - sform.s7c_e2_es)
                        data.append(max(diff, 0.15 * sform.s7c_e2_se))  # 4
                        diff = abs(sform.s7c_e3_se - sform.s7c_e3_es)
                        data.append(max(diff, 0.15 * sform.s7c_e3_se))  # 5
                        diff = abs(sform.s7d_e1_en - sform.s7d_e1_es)
                        data.append(max(diff, 0.15 * sform.s7d_e1_en))  # 6
                        data.append( '{:.2f}'.format(0.85 * sform.s8_e1_en))  # 7
                        # if (diff > 4 or diff > sform.s7d_e1_en * 0.15):  # 1
                        #     data.append(0)
                        # else:
                        #     data.append(1)

                    elif (item[1] == ECG_1):
                        template_name = 'report/ECG/licence1.html'
                        k = int(sform.s13_e1_v) * int(sform.s13_e1_a)
                        data.append(k)  # 0
                        data.append(format((2 ** 0.5) * k, '.2f'))  # 1

                    elif (item[1] == ElectroCauter_1):
                        template_name = 'report/ElectroCauter/licence1.html'
                        data.append(abs(sform.s3a_e1_m - sform.s3a_e1_s))  # 0
                        data.append(
                            (abs(sform.s3a_e1_m - sform.s3a_e1_m) / sform.s3a_e1_s) * 100)  # 1
                        data.append(abs(sform.s3a_e2_m - sform.s3a_e2_s))  # 2
                        data.append(
                            (abs(sform.s3a_e2_m - sform.s3a_e2_s) / sform.s3a_e2_s) * 100)  # 3
                        data.append(abs(sform.s3a_e3_m - sform.s3a_e3_s))  # 4
                        data.append(
                            (abs(sform.s3a_e3_m - sform.s3a_e3_s) / sform.s3a_e3_s) * 100)  # 5

                        data.append(abs(sform.s3b_e1_m - sform.s3b_e1_s))  # 6
                        data.append(
                            (abs(sform.s3b_e1_m - sform.s3b_e1_s) / sform.s3b_e1_s) * 100)  # 7
                        data.append(abs(sform.s3b_e2_m - sform.s3b_e2_s))  # 8
                        data.append(
                            (abs(sform.s3b_e2_m - sform.s3b_e2_s) / sform.s3b_e2_s) * 100)  # 9
                        data.append(abs(sform.s3b_e3_m - sform.s3b_e3_s))  # 10
                        data.append(
                            (abs(sform.s3b_e3_m - sform.s3b_e3_s) / sform.s3b_e3_s) * 100)  # 11

                        data.append('')
                        data.append('')
                        data.append('')
                        # data.append(abs(sform.s3c_e1_m - sform.s3c_e1_s))  # 12
                        # data.append(
                        #     (abs(sform.s3c_e1_m - sform.s3c_e1_s) / sform.s3c_e1_s) * 100)  # 13
                        # data.append(abs(sform.s3c_e2_m - sform.s3c_e2_s))  # 14
                        # data.append(
                        #     (abs(sform.s3c_e2_m - sform.s3c_e2_s) / sform.s3c_e2_s) * 100)  # 15
                        # data.append(abs(sform.s3c_e3_m - sform.s3c_e3_s))  # 16
                        # data.append(
                        #     (abs(sform.s3c_e3_m - sform.s3c_e3_s) / sform.s3c_e3_s) * 100)  # 17

                        data.append(abs(sform.s3d_e1_m - sform.s3d_e1_s))  # 18
                        data.append(
                            (abs(sform.s3d_e1_m - sform.s3d_e1_s) / sform.s3d_e1_s) * 100)  # 19
                        data.append(abs(sform.s3d_e2_m - sform.s3d_e2_s))  # 20
                        data.append(
                            (abs(sform.s3d_e2_m - sform.s3d_e2_s) / sform.s3d_e2_s) * 100)  # 21
                        data.append(abs(sform.s3d_e3_m - sform.s3d_e3_s))  # 22
                        data.append(
                            (abs(sform.s3d_e3_m - sform.s3d_e3_s) / sform.s3d_e3_s) * 100)  # 23

                        data.append(abs(sform.s3e_e1_m - sform.s3e_e1_s))  # 24
                        data.append(
                            (abs(sform.s3e_e1_m - sform.s3e_e1_s) / sform.s3e_e1_s) * 100)  # 25
                        data.append(abs(sform.s3e_e2_m - sform.s3e_e2_s))  # 26
                        data.append(
                            (abs(sform.s3e_e2_m - sform.s3e_e2_s) / sform.s3e_e2_s) * 100)  # 27
                        data.append(abs(sform.s3e_e3_m - sform.s3e_e3_s))  # 28
                        data.append(
                            (abs(sform.s3e_e3_m - sform.s3e_e3_s) / sform.s3e_e3_s) * 100)  # 29

                    elif (item[1] == FlowMeter_1):
                        template_name = 'report/FlowMeter/licence1.html'
                        data.append(round(abs(float(sform.s1_e1_rlpm) - 0.5), 2))  # 0
                        data.append(round(abs(float(sform.s1_e2_rlpm) - 2), 2))  # 1
                        data.append(round(abs(float(sform.s1_e3_rlpm) - 4), 2))  # 2
                        data.append(round(abs(float(sform.s1_e4_rlpm) - 7), 2))  # 3
                        data.append(round(abs(float(sform.s1_e5_rlpm) - 10), 2))  # 4
                        data.append(round(abs(float(sform.s1_e6_rlpm) - 15), 2))  # 5
                        data.append(round(float(data[0]) * 200, 2))  # 6
                        data.append(round(float(data[1]) * 50, 2))  # 7
                        data.append(round(float(data[2]) * 25, 2))  # 8
                        data.append(round(float(data[3]) * (100/7), 2))  # 9
                        data.append(round(float(data[4]) * 10, 2))  # 10
                        data.append(round(float(data[5]) * (100/15), 2))  # 11

                    elif (item[1] == InfusionPump_1):
                        template_name = 'report/InfusionPump/licence1.html'
                        data.append(abs((int(sform.s6_e1_mf) - 50)*2))  # 0
                        data.append(abs(int(sform.s6_e2_mf) - 100))  # 1

                    elif (item[1] == ManoMeter_1):
                        template_name = 'report/ManoMeter/licence1.html'
                        data.append(abs(sform.s2_e1_sp - sform.s2_e1_np))  # 0
                        data.append(abs(sform.s2_e2_sp - sform.s2_e2_np))  # 1
                        data.append(abs(sform.s2_e3_sp - sform.s2_e3_np))  # 2
                        data.append(abs(sform.s2_e4_sp - sform.s2_e4_np))  # 3

                    elif (item[1] == Spo2_1):
                        template_name = 'report/spo2/licence1.html'
                        ss = 0
                        sss = 0
                        data.append((int(sform.s2_e1_spo2) - 70)**2)  # 0
                        data.append((int(sform.s2_e2_spo2) - 75)**2)  # 1
                        data.append((int(sform.s2_e3_spo2) - 80)**2)  # 2
                        data.append((int(sform.s2_e4_spo2) - 85)**2)  # 3
                        data.append((int(sform.s2_e5_spo2) - 88)**2)  # 4
                        data.append((int(sform.s2_e6_spo2) - 90)**2)  # 5
                        data.append((int(sform.s2_e7_spo2) - 92)**2)  # 6
                        data.append((int(sform.s2_e8_spo2) - 94)**2)  # 7
                        data.append((int(sform.s2_e9_spo2) - 96)**2)  # 8
                        data.append((int(sform.s2_e10_spo2) - 98)**2)  # 9
                        data.append((int(sform.s2_e11_spo2) - 100)**2)  # 10
                        for i in range(11):
                            ss += data[i]
                        data.append(int(((ss/11)**0.5)*100)/100)  # 11

                        data.append((int(sform.s3_e1_pr) - 35)**2)  # 12
                        data.append((int(sform.s3_e2_pr) - 60)**2)  # 13
                        data.append((int(sform.s3_e3_pr) - 100)**2)  # 14
                        data.append((int(sform.s3_e4_pr) - 200)**2)  # 15
                        data.append((int(sform.s3_e5_pr) - 240)**2)  # 16
                        for i in range(12, 17):
                            sss += data[i]
                        data.append(int(((sss/5)**0.5)*100)/100)  # 17
                        k = int(sform.s5_e1_v) * int(sform.s5_e1_a)
                        data.append(k)  # 18
                        data.append(format((2 ** 0.5) * k, '.2f'))  # 19

                    elif (item[1] == Suction_1):
                        template_name = 'report/Suction/licence1.html'
                        data.append(abs(int(sform.s1_e1_rr)))  # 0
                        data.append(abs(int(sform.s1_e2_rr)))  # 1
                        data.append(abs(int(sform.s1_e3_rr) - 100))  # 2
                        data.append(abs(int(sform.s1_e4_rr) - 0.1))  # 3
                        data.append(abs(int(sform.s1_e5_rr) - 200))  # 4
                        data.append(abs(int(sform.s1_e6_rr - 0.3)))  # 5
                        data.append(abs(int(sform.s1_e7_rr) - 400))  # 6
                        data.append(abs(int(sform.s1_e8_rr) - 0.5))  # 7
                        data.append(abs(int(sform.s1_e9_rr) - 500))  # 8
                        data.append(abs(int(sform.s1_e10_rr) - 0.7))  # 9
                        data.append(abs(int(sform.s2_e1_rr)))  # 10/////
                        data.append(abs(int(sform.s2_e2_rr)))  # 11
                        data.append(abs(int(sform.s2_e2_rr) - 38))  # 12
                        data.append(abs(int(sform.s2_e2_rr) - 50))  # 13
                        data.append(abs(int(sform.s2_e2_rr) - 76))  # 14
                        data.append(abs(int(sform.s2_e2_rr) - 100))  # 15
                        data.append(abs(int(sform.s2_e2_rr) - 114))  # 16
                        data.append(abs(int(sform.s2_e2_rr) - 150))  # 17

                    elif (item[1] == SyringePump_1):
                        template_name = 'report/SyringePump/licence1.html'
                        data.append(abs((int(sform.s6_e1_mf) - 50)*2))  # 0
                        data.append(abs(int(sform.s6_e2_mf) - 100))  # 1

                    elif (item[1] == Ventilator_1):
                        template_name = 'report/Ventilator/licence1.html'
                        if sform.s16_e1 <= 550 and sform.s16_e1 >= 450:  # 0
                            data.append(1)
                        else:
                            data.append(0)
                        if sform.s16_e2 <= 13.2 and sform.s16_e2 >= 10.8:  # 1
                            data.append(1)
                        else:
                            data.append(0)
                        if sform.s16_1e1 != -1:  # 2
                            if sform.s16_e3 <= (sform.s16_1e1 * 1.1) and sform.s16_e3 >= (sform.s16_1e1 * 0.9):
                                data.append(1)
                            else:
                                data.append(0)
                        else:
                            data.append(2)
                        if sform.s16_1e2 != -1:  # 3
                            if sform.s16_e4 <= (sform.s16_1e2 * 1.1) and sform.s16_e4 >= (sform.s16_1e2 * 0.9):
                                data.append(1)
                            else:
                                data.append(0)
                        else:
                            data.append(2)
                        if sform.s16_e5 <= 0.55 and sform.s16_e5 >= 0.45:  # 4
                            data.append(1)
                        else:
                            data.append(0)
                        if sform.s16_e6 <= 22 and sform.s16_e6 >= 18:  # 5
                            data.append(1)
                        else:
                            data.append(0)
                        if sform.s16_1e3 != -1:  # 6
                            if sform.s16_e7 <= (sform.s16_1e3 * 1.1) and sform.s16_e7 >= (sform.s16_1e3 * 0.9):
                                data.append(1)
                            else:
                                data.append(0)
                        else:
                            data.append(2)

                    user_profile = UserProfile.objects.get(user=sform.user)
                    today_datetime = jdatetime.datetime.today()
                    font_config = FontConfiguration()
                    html = render_to_string(template_name, {
                        'form': sform, 'time': today_datetime, 'user_profile': user_profile, 'data': data, 'domain_name': domain_name})
                    
                    if DEBUG:
                        css_root = STATICFILES_DIRS[0] + '\css'
                    else:
                        css_root = STATIC_ROOT + '/css'

                    css1 = CSS(
                        filename=f'{css_root}/sop2-pdf.css')
                    css2 = CSS(
                        filename=f'{css_root}/bootstrap-v4.min.css')
                    report_name = 'report_{}.pdf'.format(sform.record.number)

                    HTML(string=html).write_pdf(
                        report_name, font_config=font_config, stylesheets=[css1, css2])
                    # ===================================End-File Backing=================================================

                    # ===================================Begin-File Processing=================================================

                    encode_query = Encode.objects.filter(
                        hospital=sform.device.hospital)
                    if len(encode_query) == 0:
                        filename = '12' + str(sform.device.hospital.user.id)
                        filename = hashlib.md5(
                            filename.encode()).hexdigest()
                        encode_instance = Encode.objects.create(
                            hospital=sform.device.hospital, name=filename)
                        encode_instance.save()
                    else:
                        filename = encode_query[0].name
                    
                    #===================================Begin-FTP Stuf=================================================
                    if not DEBUG:
                        with FTP(
                            host=DL_FTP_HOST,
                            user=DL_FTP_USER,
                            passwd=DL_FTP_PASSWD
                        ) as ftp:
                            ftp.cwd('pdf')
                            if not sform.device.hospital.city.state.eng_name in ftp.nlst():
                                ftp.mkd(sform.device.hospital.city.state.eng_name)
                            ftp.cwd(sform.device.hospital.city.state.eng_name)
                            if not sform.device.hospital.city.eng_name in ftp.nlst():
                                ftp.mkd(sform.device.hospital.city.eng_name)
                            ftp.cwd(sform.device.hospital.city.eng_name)
                            if not str(sform.device.hospital.id) + '_' + filename in ftp.nlst():
                                ftp.mkd(str(sform.device.hospital.id) +
                                        '_' + filename)
                            ftp.cwd(str(sform.device.hospital.id) + '_' + filename)
                            if not str(sform.request.number) in ftp.nlst():
                                ftp.mkd(str(sform.request.number))
                            ftp.cwd(str(sform.request.number))

                            if not str(sform.device.section.eng_name) in ftp.nlst():
                                ftp.mkd(str(sform.device.section.eng_name))
                            ftp.cwd(str(sform.device.section.eng_name))

                            if not item[0] in ftp.nlst():
                                ftp.mkd(item[0])

                            ftp.cwd(item[0])

                            send_file_ftp(
                                ftp, '{}.pdf'.format(sform.licence.number), report_name)
                            os.remove(report_name)
                            
                            ftp.close()
                    # ===================================End-FTP Stuf=================================================
                    
                    
                    green_status += 'PDF ذخیره شد!!!'
                    report_query = Report.objects.filter(record=sform.record)
                    if len(report_query):
                        report_query[0].delete()
                    report_instance = Report.objects.create(tt=AdTestType0.objects.get(type=(item[0] if item[0] != 'spo2' else 'PulseOximetry')), device=sform.device,
                                                            request=sform.request, date=sform.date, user=sform.user, status=sform.status,
                                                            record=sform.record, licence=sform.licence, is_recal=sform.is_recal, ref_record=sform.ref_record,
                                                            is_done=sform.is_done, totalcomment=sform.totalcomment)
                    report_instance.save()
                    # except:
                    #     return HttpResponse('Error while sending to host!!!!')
                    return render(request, 'acc/employee/index.html',
                                  {'green_status': green_status, 'user_name': request.user.first_name, 'avatar_url': avatar_url, })
                else:  # form imcomplete
                    return render(request, 'acc/employee/index.html',
                                  {'form': form1, 'red_status': 'اطلاعات ناقص است!', 'form_type': item[0], 'user_name': request.user.first_name, 'avatar_url': avatar_url, })
    else:
        raise Http404


def reload(request, formtype):
    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(name='employee') in request.user.groups.all():
        avatar_url = UserProfile.objects.get(
            id=1).avatar.url  # admin user_profile
        for item in model_list:
            if formtype == item[0]:
                form1 = item[2](request.POST)
                return render(request, 'acc/employee/index.html',
                    {'form': form1, 'form_type': item[0], 'user_name': request.user.first_name, 'avatar_url': avatar_url, 'reload': 1})
