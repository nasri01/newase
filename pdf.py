import hashlib
import os
from ftplib import FTP
from statistics import mean, stdev

import jdatetime
import pytz
from django.template.loader import render_to_string
from weasyprint import CSS, HTML
from weasyprint.fonts import FontConfiguration

from acc.models import AdTestType0, CalDevice, Licence, Record, UserProfile
from acc.views import model_dict
from report.models import Encode, Report
from ww.local_settings import (DEBUG, DL_FTP_HOST, DL_FTP_PASSWD, DL_FTP_USER,
                               domain_name)
from ww.settings import STATIC_ROOT, STATICFILES_DIRS
from form.models import *



def send_file_ftp(ftp_obj, filename, report_name):
    fp = open(report_name, 'rb')
    ftp_obj.storbinary('STOR %s' % os.path.basename(filename), fp, 8192)


for t, model_hist in model_dict.items():
    for item in model_hist:
        query = item[0].objects.filter(has_pdf=False).filter(
            date__gte=(jdatetime.datetime.today()-jdatetime.timedelta(days=365)).astimezone(pytz.timezone('Asia/Tehran')))
        for idx, obj in enumerate(query):
            print('[{}/{}] -> Start'.format(idx, len(query)))
            data = []
            if item[0] != CantTest:

                if item[0] == MonitorSpo2_1:
                    template_name = 'report/Monitor/Spo2/licence1.html'
                    ss = 0
                    sss = 0
                    data.append((int(obj.s2_e1_spo2) - 70) ** 2)  # 0
                    data.append((int(obj.s2_e2_spo2) - 75) ** 2)  # 1
                    data.append((int(obj.s2_e3_spo2) - 80) ** 2)  # 2
                    data.append((int(obj.s2_e4_spo2) - 85) ** 2)  # 3
                    data.append((int(obj.s2_e5_spo2) - 88) ** 2)  # 4
                    data.append((int(obj.s2_e6_spo2) - 90) ** 2)  # 5
                    data.append((int(obj.s2_e7_spo2) - 92) ** 2)  # 6
                    data.append((int(obj.s2_e8_spo2) - 94) ** 2)  # 7
                    data.append((int(obj.s2_e9_spo2) - 96) ** 2)  # 8
                    data.append((int(obj.s2_e10_spo2) - 98) ** 2)  # 9
                    data.append((int(obj.s2_e11_spo2) - 100) ** 2)  # 10
                    for i in range(11):
                        ss += data[i]
                    data.append(int(((ss / 11) ** 0.5) * 100) / 100)  # 11

                    data.append((int(obj.s3_e1_pr) - 35) ** 2)  # 12
                    data.append((int(obj.s3_e2_pr) - 60) ** 2)  # 13
                    data.append((int(obj.s3_e3_pr) - 100) ** 2)  # 14
                    data.append((int(obj.s3_e4_pr) - 200) ** 2)  # 15
                    data.append((int(obj.s3_e5_pr) - 240) ** 2)  # 16
                    for i in range(12, 17):
                        sss += data[i]
                    data.append(int(((sss / 5) ** 0.5) * 100) / 100)  # 17

                elif item[0] == MonitorNIBP_1:
                    template_name = 'report/Monitor/NIBP/licence1.html'
                    data1 = []
                    data2 = []
                    data3 = []

                    data3.append(
                        0 if abs(int(obj.s1_e1_simp) - int(obj.s1_e1_nibpp)) >= max(3, int(
                            obj.s1_e1_simp) * 0.03) else 1)
                    data3.append(
                        0 if abs(int(obj.s1_e1_simp) - int(obj.s1_e1_nibpp)) >= max(3, int(
                            obj.s1_e1_simp) * 0.03) else 1)
                    data3.append(
                        0 if abs(int(obj.s1_e1_simp) - int(obj.s1_e1_nibpp)) >= max(3, int(
                            obj.s1_e1_simp) * 0.03) else 1)
                    data3.append(
                        0 if abs(int(obj.s1_e1_simp) - int(obj.s1_e1_nibpp)) >= max(3, int(
                            obj.s1_e1_simp) * 0.03) else 1)
                    data3.append(
                        0 if abs(int(obj.s1_e1_simp) - int(obj.s1_e1_nibpp)) >= max(3, int(
                            obj.s1_e1_simp) * 0.03) else 1)
                    data3.append(
                        0 if abs(int(obj.s1_e1_simp) - int(obj.s1_e1_nibpp)) >= max(3, int(
                            obj.s1_e1_simp) * 0.03) else 1)
                    data3.append(
                        0 if abs(int(obj.s1_e1_simp) - int(obj.s1_e1_nibpp)) >= max(3, int(
                            obj.s1_e1_simp) * 0.03) else 1)
                    data3.append(
                        0 if abs(int(obj.s1_e1_simp) - int(obj.s1_e1_nibpp)) >= max(3, int(
                            obj.s1_e1_simp) * 0.03) else 1)

                    data1.append(int(obj.s2_e1_pr1.split('/')[0]))
                    data1.append(int(obj.s2_e1_pr2.split('/')[0]))
                    data1.append(int(obj.s2_e1_pr3.split('/')[0]))
                    data1.append(int(obj.s2_e2_pr1.split('/')[0]))
                    data1.append(int(obj.s2_e2_pr2.split('/')[0]))
                    data1.append(int(obj.s2_e2_pr3.split('/')[0]))
                    data1.append(int(obj.s2_e3_pr1.split('/')[0]))
                    data1.append(int(obj.s2_e3_pr2.split('/')[0]))
                    data1.append(int(obj.s2_e3_pr3.split('/')[0]))
                    data1.append(int(obj.s2_e4_pr1.split('/')[0]))
                    data1.append(int(obj.s2_e4_pr2.split('/')[0]))
                    data1.append(int(obj.s2_e4_pr3.split('/')[0]))
                    data1.append(int(obj.s2_e5_pr1.split('/')[0]))
                    data1.append(int(obj.s2_e5_pr2.split('/')[0]))
                    data1.append(int(obj.s2_e5_pr3.split('/')[0]))
                    data1.append(int(obj.s2_e6_pr1.split('/')[0]))
                    data1.append(int(obj.s2_e6_pr2.split('/')[0]))
                    data1.append(int(obj.s2_e6_pr3.split('/')[0]))
                    data2.append(int(obj.s2_e1_pr1.split('/')[1]))
                    data2.append(int(obj.s2_e1_pr2.split('/')[1]))
                    data2.append(int(obj.s2_e1_pr3.split('/')[1]))
                    data2.append(int(obj.s2_e2_pr1.split('/')[1]))
                    data2.append(int(obj.s2_e2_pr2.split('/')[1]))
                    data2.append(int(obj.s2_e2_pr3.split('/')[1]))
                    data2.append(int(obj.s2_e3_pr1.split('/')[1]))
                    data2.append(int(obj.s2_e3_pr2.split('/')[1]))
                    data2.append(int(obj.s2_e3_pr3.split('/')[1]))
                    data2.append(int(obj.s2_e4_pr1.split('/')[1]))
                    data2.append(int(obj.s2_e4_pr2.split('/')[1]))
                    data2.append(int(obj.s2_e4_pr3.split('/')[1]))
                    data2.append(int(obj.s2_e5_pr1.split('/')[1]))
                    data2.append(int(obj.s2_e5_pr2.split('/')[1]))
                    data2.append(int(obj.s2_e5_pr3.split('/')[1]))
                    data2.append(int(obj.s2_e6_pr1.split('/')[1]))
                    data2.append(int(obj.s2_e6_pr2.split('/')[1]))
                    data2.append(int(obj.s2_e6_pr3.split('/')[1]))

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

                elif item[0] == MonitorECG_1:
                    template_name = 'report/Monitor/ECG/licence1.html'

                elif item[0] == MonitorSafety_1:
                    template_name = 'report/Monitor/SAFETY/licence1.html'

                elif item[0] == AED_1:
                    template_name = 'report/AED/licence1.html'

                elif item[0] == AnesthesiaMachine_1:
                    template_name = 'report/AnesthesiaMachine/licence1.html'

                elif item[0] == Defibrilator_1:
                    template_name = 'report/Defibrilator/licence1.html'

                    diff = abs(obj.s7a_e1_se - obj.s7a_e1_es)
                    data.append(max(diff, 0.15 * obj.s7a_e1_se))  # 0
                    diff = abs(obj.s7a_e2_se - obj.s7a_e2_es)
                    data.append(max(diff, 0.15 * obj.s7a_e2_se))  # 1
                    diff = abs(obj.s7a_e3_se - obj.s7a_e3_es)
                    data.append(max(diff, 0.15 * obj.s7a_e3_se))  # 2

                    diff = abs(obj.s7c_e1_se - obj.s7c_e1_es)
                    data.append(max(diff, 0.15 * obj.s7c_e1_se))  # 3
                    diff = abs(obj.s7c_e2_se - obj.s7c_e2_es)
                    data.append(max(diff, 0.15 * obj.s7c_e2_se))  # 4
                    diff = abs(obj.s7c_e3_se - obj.s7c_e3_es)
                    data.append(max(diff, 0.15 * obj.s7c_e3_se))  # 5
                    diff = abs(obj.s7d_e1_en - obj.s7d_e1_es)
                    data.append(max(diff, 0.15 * obj.s7d_e1_en))  # 6
                    data.append('{:.2f}'.format(0.85 * obj.s8_e1_en))  # 7
                    # if (diff > 4 or diff > obj.s7d_e1_en * 0.15):  # 1
                    #     data.append(0)
                    # else:
                    #     data.append(1)

                elif item[0] == ECG_1:
                    template_name = 'report/ECG/licence1.html'
                    k = int(obj.s13_e1_v) * int(obj.s13_e1_a)
                    data.append(k)  # 0
                    data.append(format((2 ** 0.5) * k, '.2f'))  # 1

                elif item[0] == ElectroCauter_1:
                    template_name = 'report/ElectroCauter/licence1.html'
                    data.append(abs(obj.s3a_e1_m - obj.s3a_e1_s))  # 0
                    data.append(
                        (abs(obj.s3a_e1_m - obj.s3a_e1_m) / obj.s3a_e1_s) * 100)  # 1
                    data.append(abs(obj.s3a_e2_m - obj.s3a_e2_s))  # 2
                    data.append(
                        (abs(obj.s3a_e2_m - obj.s3a_e2_s) / obj.s3a_e2_s) * 100)  # 3
                    data.append(abs(obj.s3a_e3_m - obj.s3a_e3_s))  # 4
                    data.append(
                        (abs(obj.s3a_e3_m - obj.s3a_e3_s) / obj.s3a_e3_s) * 100)  # 5

                    data.append(abs(obj.s3b_e1_m - obj.s3b_e1_s))  # 6
                    data.append(
                        (abs(obj.s3b_e1_m - obj.s3b_e1_s) / obj.s3b_e1_s) * 100)  # 7
                    data.append(abs(obj.s3b_e2_m - obj.s3b_e2_s))  # 8
                    data.append(
                        (abs(obj.s3b_e2_m - obj.s3b_e2_s) / obj.s3b_e2_s) * 100)  # 9
                    data.append(abs(obj.s3b_e3_m - obj.s3b_e3_s))  # 10
                    data.append(
                        (abs(obj.s3b_e3_m - obj.s3b_e3_s) / obj.s3b_e3_s) * 100)  # 11

                    data.append('')
                    data.append('')
                    data.append('')
                    # data.append(abs(obj.s3c_e1_m - obj.s3c_e1_s))  # 12
                    # data.append(
                    #     (abs(obj.s3c_e1_m - obj.s3c_e1_s) / obj.s3c_e1_s) * 100)  # 13
                    # data.append(abs(obj.s3c_e2_m - obj.s3c_e2_s))  # 14
                    # data.append(
                    #     (abs(obj.s3c_e2_m - obj.s3c_e2_s) / obj.s3c_e2_s) * 100)  # 15
                    # data.append(abs(obj.s3c_e3_m - obj.s3c_e3_s))  # 16
                    # data.append(
                    #     (abs(obj.s3c_e3_m - obj.s3c_e3_s) / obj.s3c_e3_s) * 100)  # 17

                    data.append(abs(obj.s3d_e1_m - obj.s3d_e1_s))  # 18
                    data.append(
                        (abs(obj.s3d_e1_m - obj.s3d_e1_s) / obj.s3d_e1_s) * 100)  # 19
                    data.append(abs(obj.s3d_e2_m - obj.s3d_e2_s))  # 20
                    data.append(
                        (abs(obj.s3d_e2_m - obj.s3d_e2_s) / obj.s3d_e2_s) * 100)  # 21
                    data.append(abs(obj.s3d_e3_m - obj.s3d_e3_s))  # 22
                    data.append(
                        (abs(obj.s3d_e3_m - obj.s3d_e3_s) / obj.s3d_e3_s) * 100)  # 23

                    data.append(abs(obj.s3e_e1_m - obj.s3e_e1_s))  # 24
                    data.append(
                        (abs(obj.s3e_e1_m - obj.s3e_e1_s) / obj.s3e_e1_s) * 100)  # 25
                    data.append(abs(obj.s3e_e2_m - obj.s3e_e2_s))  # 26
                    data.append(
                        (abs(obj.s3e_e2_m - obj.s3e_e2_s) / obj.s3e_e2_s) * 100)  # 27
                    data.append(abs(obj.s3e_e3_m - obj.s3e_e3_s))  # 28
                    data.append(
                        (abs(obj.s3e_e3_m - obj.s3e_e3_s) / obj.s3e_e3_s) * 100)  # 29

                elif item[0] == FlowMeter_1:
                    template_name = 'report/FlowMeter/licence1.html'
                    data.append(round(abs(float(obj.s1_e1_rlpm) - 0.5), 2))  # 0
                    data.append(round(abs(float(obj.s1_e2_rlpm) - 2), 2))  # 1
                    data.append(round(abs(float(obj.s1_e3_rlpm) - 4), 2))  # 2
                    data.append(round(abs(float(obj.s1_e4_rlpm) - 7), 2))  # 3
                    data.append(round(abs(float(obj.s1_e5_rlpm) - 10), 2))  # 4
                    data.append(round(abs(float(obj.s1_e6_rlpm) - 15), 2))  # 5
                    data.append(round(float(data[0]) * 200, 2))  # 6
                    data.append(round(float(data[1]) * 50, 2))  # 7
                    data.append(round(float(data[2]) * 25, 2))  # 8
                    data.append(round(float(data[3]) * (100 / 7), 2))  # 9
                    data.append(round(float(data[4]) * 10, 2))  # 10
                    data.append(round(float(data[5]) * (100 / 15), 2))  # 11

                elif item[0] == InfusionPump_1:
                    template_name = 'report/InfusionPump/licence1.html'
                    data.append(abs((int(obj.s6_e1_mf) - 50) * 2))  # 0
                    data.append(abs(int(obj.s6_e2_mf) - 100))  # 1

                elif item[0] == ManoMeter_1:
                    template_name = 'report/ManoMeter/licence1.html'
                    data.append(abs(obj.s2_e1_sp - obj.s2_e1_np))  # 0
                    data.append(abs(obj.s2_e2_sp - obj.s2_e2_np))  # 1
                    data.append(abs(obj.s2_e3_sp - obj.s2_e3_np))  # 2
                    data.append(abs(obj.s2_e4_sp - obj.s2_e4_np))  # 3

                elif item[0] == Spo2_1:
                    template_name = 'report/spo2/licence1.html'
                    ss = 0
                    sss = 0
                    data.append((int(obj.s2_e1_spo2) - 70) ** 2)  # 0
                    data.append((int(obj.s2_e2_spo2) - 75) ** 2)  # 1
                    data.append((int(obj.s2_e3_spo2) - 80) ** 2)  # 2
                    data.append((int(obj.s2_e4_spo2) - 85) ** 2)  # 3
                    data.append((int(obj.s2_e5_spo2) - 88) ** 2)  # 4
                    data.append((int(obj.s2_e6_spo2) - 90) ** 2)  # 5
                    data.append((int(obj.s2_e7_spo2) - 92) ** 2)  # 6
                    data.append((int(obj.s2_e8_spo2) - 94) ** 2)  # 7
                    data.append((int(obj.s2_e9_spo2) - 96) ** 2)  # 8
                    data.append((int(obj.s2_e10_spo2) - 98) ** 2)  # 9
                    data.append((int(obj.s2_e11_spo2) - 100) ** 2)  # 10
                    for i in range(11):
                        ss += data[i]
                    data.append(int(((ss / 11) ** 0.5) * 100) / 100)  # 11

                    data.append((int(obj.s3_e1_pr) - 35) ** 2)  # 12
                    data.append((int(obj.s3_e2_pr) - 60) ** 2)  # 13
                    data.append((int(obj.s3_e3_pr) - 100) ** 2)  # 14
                    data.append((int(obj.s3_e4_pr) - 200) ** 2)  # 15
                    data.append((int(obj.s3_e5_pr) - 240) ** 2)  # 16
                    for i in range(12, 17):
                        sss += data[i]
                    data.append(int(((sss / 5) ** 0.5) * 100) / 100)  # 17

                    if (int(obj.s5_e1_v) != -1):
                        k = int(obj.s5_e1_v) * int(obj.s5_e1_a)
                    else:
                        k = -1
                    data.append(k)  # 18

                    if (int(obj.s5_e1_v) != -1):
                        data.append(format((2 ** 0.5) * k, '.2f'))  # 19
                    else:
                        data.append(-1)  # 19

                    if (obj.s6_e1_er == -1):  # for N/A of Section 6
                        data.append(1)  # 20
                    else:
                        data.append(0)

                elif item[0] == Suction_1:
                    template_name = 'report/Suction/licence1.html'
                    data.append(abs(int(obj.s1_e1_rr))) if obj.s1_e1_rr != None else data.append('')  # 0
                    data.append(abs(int(obj.s1_e2_rr))) if obj.s1_e2_rr != None else data.append('')  # 1
                    data.append(abs(int(obj.s1_e3_rr) - 100)) if obj.s1_e3_rr != None else data.append('')  # 2
                    data.append(abs(int(obj.s1_e4_rr) - 0.1)) if obj.s1_e4_rr != None else data.append('')  # 3
                    data.append(abs(int(obj.s1_e5_rr) - 200)) if obj.s1_e5_rr != None else data.append('')  # 4
                    data.append(abs(int(obj.s1_e6_rr - 0.3))) if obj.s1_e6_rr != None else data.append('')  # 5
                    data.append(abs(int(obj.s1_e7_rr) - 400)) if obj.s1_e7_rr != None else data.append('')  # 6
                    data.append(abs(int(obj.s1_e8_rr) - 0.5)) if obj.s1_e8_rr != None else data.append('')  # 7
                    data.append(abs(int(obj.s1_e9_rr) - 500)) if obj.s1_e9_rr != None else data.append('')  # 8
                    data.append(abs(int(obj.s1_e10_rr) - 0.7)) if obj.s1_e10_rr != None else data.append('')  # 9
                    data.append(abs(int(obj.s2_e1_rr))) if obj.s2_e1_rr != None else data.append('')  # 10/////
                    data.append(abs(int(obj.s2_e2_rr))) if obj.s2_e2_rr != None else data.append('')  # 11
                    data.append(abs(int(obj.s2_e3_rr) - 38)) if obj.s2_e3_rr != None else data.append('')  # 12
                    data.append(abs(int(obj.s2_e4_rr) - 50)) if obj.s2_e4_rr != None else data.append('')  # 13
                    data.append(abs(int(obj.s2_e5_rr) - 76)) if obj.s2_e5_rr != None else data.append('')  # 14
                    data.append(abs(int(obj.s2_e6_rr) - 100)) if obj.s2_e6_rr != None else data.append('')  # 15
                    data.append(abs(int(obj.s2_e7_rr) - 114)) if obj.s2_e7_rr != None else data.append('')  # 16
                    data.append(abs(int(obj.s2_e8_rr) - 150)) if obj.s2_e8_rr != None else data.append('')  # 17

                elif item[0] == SyringePump_1:
                    template_name = 'report/SyringePump/licence1.html'
                    data.append(abs((int(obj.s6_e1_mf) - 50) * 2))  # 0
                    data.append(abs(int(obj.s6_e2_mf) - 100))  # 1

                elif item[0] == Ventilator_1:
                    template_name = 'report/Ventilator/licence1.html'
                    if obj.s16_e1 <= 550 and obj.s16_e1 >= 450:  # 0
                        data.append(1)
                    else:
                        data.append(0)
                    if obj.s16_e2 <= 13.2 and obj.s16_e2 >= 10.8:  # 1
                        data.append(1)
                    else:
                        data.append(0)
                    if obj.s16_1e1 != -1:  # 2
                        if obj.s16_e3 <= (obj.s16_1e1 * 1.1) and obj.s16_e3 >= (obj.s16_1e1 * 0.9):
                            data.append(1)
                        else:
                            data.append(0)
                    else:
                        data.append(2)
                    if obj.s16_1e2 != -1:  # 3
                        if obj.s16_e4 <= (obj.s16_1e2 * 1.1) and obj.s16_e4 >= (obj.s16_1e2 * 0.9):
                            data.append(1)
                        else:
                            data.append(0)
                    else:
                        data.append(2)
                    if obj.s16_e5 <= 0.55 and obj.s16_e5 >= 0.45:  # 4
                        data.append(1)
                    else:
                        data.append(0)
                    if obj.s16_e6 <= 22 and obj.s16_e6 >= 18:  # 5
                        data.append(1)
                    else:
                        data.append(0)
                    if obj.s16_1e3 != -1:  # 6
                        if obj.s16_e7 <= (obj.s16_1e3 * 1.1) and obj.s16_e7 >= (obj.s16_1e3 * 0.9):
                            data.append(1)
                        else:
                            data.append(0)
                    else:
                        data.append(2)

                encode_query = Encode.objects.filter(
                    hospital=obj.device.hospital)
                if len(encode_query) == 0:
                    filename = '12' + str(obj.device.hospital.user.id)
                    filename = hashlib.md5(
                        filename.encode()).hexdigest()
                    encode_instance = Encode.objects.create(
                        hospital=obj.device.hospital, name=filename)
                    encode_instance.save()
                else:
                    filename = encode_query[0].name

                with FTP(host=DL_FTP_HOST, user=DL_FTP_USER, passwd=DL_FTP_PASSWD) as ftp:
                    print('[{}/{}] -> FTP in!'.format(idx, len(query)))
                    ftp.cwd('pdf')
                    if not obj.device.hospital.city.state.eng_name in ftp.nlst():
                        ftp.mkd(obj.device.hospital.city.state.eng_name)
                    ftp.cwd(obj.device.hospital.city.state.eng_name)
                    if not obj.device.hospital.city.eng_name in ftp.nlst():
                        ftp.mkd(obj.device.hospital.city.eng_name)
                    ftp.cwd(obj.device.hospital.city.eng_name)
                    if not str(obj.device.hospital.user.id) + '_' + filename in ftp.nlst():
                        ftp.mkd(str(obj.device.hospital.user.id) +
                                '_' + filename)
                    ftp.cwd(str(obj.device.hospital.user.id) + '_' + filename)
                    if not str(obj.request.number) in ftp.nlst():
                        ftp.mkd(str(obj.request.number))
                    ftp.cwd(str(obj.request.number))

                    if not str(obj.device.section.eng_name) in ftp.nlst():
                        ftp.mkd(str(obj.device.section.eng_name))
                    ftp.cwd(str(obj.device.section.eng_name))

                    if not t in ftp.nlst():
                        ftp.mkd(t)

                    ftp.cwd(t)

                    if not '{}.pdf'.format(obj.licence.number) in ftp.nlst():
                        #====================================/ Start Making PDF /======================
                        print('getready{}'.format(obj.licence.number))
                        user_profile = UserProfile.objects.get(user=obj.user)
                        today_datetime = obj.date
                        # today_datetime = jdatetime.datetime.today()
                        font_config = FontConfiguration()
                        html = render_to_string(template_name, {
                            'form': obj, 'time': today_datetime, 'user_profile': user_profile, 'data': data,
                            'domain_name': domain_name})
                        if DEBUG:
                            css_root = STATICFILES_DIRS[0] + '/css'
                        else:
                            css_root = STATIC_ROOT + '/css'

                        css1 = CSS(
                            filename=f'{css_root}/sop2-pdf.css')
                        css2 = CSS(
                            filename=f'{css_root}/bootstrap-v4.min.css')
                        report_name = 'report_{}.pdf'.format(obj.record.number)
                        print('[{}/{}] -> pdfStart'.format(idx, len(query)))
                        HTML(string=html).write_pdf(
                            report_name, font_config=font_config, stylesheets=[css1, css2])
                        print('[{}/{}] -> pdfEnd'.format(idx, len(query)))

                        send_file_ftp(
                            ftp, '{}.pdf'.format(obj.licence.number), report_name)
                        print('[{}/{}] -> FileSent'.format(idx, len(query)))

                        obj.has_pdf = True
                        obj.save()

                        os.remove(report_name)
                    ftp.close()




            report_query = Report.objects.filter(record=obj.record)
            if not len(report_query):
                report_instance = Report.objects.create(
                    tt=AdTestType0.objects.get(type=(t if t != 'spo2' else 'PulseOximetry')),
                    device=obj.device,
                    request=obj.request, date=obj.date, user=obj.user, status=obj.status,
                    record=obj.record,
                    licence=obj.licence if t != 'CantTest' else Licence.objects.get(number=-1),
                    is_recal=obj.is_recal,
                    ref_record=obj.ref_record if item[0] != CantTest else Record.objects.get(number=-1),
                    is_done=obj.is_done, totalcomment=obj.totalcomment)
                report_instance.save()
                print('[{}/{}] -> ReportCreated! - {}'.format(idx, len(query), report_instance.id))
            # except:
            #     return HttpResponse('Error while sending to host!!!!')
