import hashlib
import io
import os
from ftplib import FTP
from statistics import mean, stdev

import jdatetime
import pytz
import weasyprint
import xlsxwriter
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.shortcuts import Http404, redirect, render
from django.template.loader import render_to_string
from django.templatetags import static
from jdatetime import timedelta
from weasyprint import CSS, HTML
from weasyprint.fonts import FontConfiguration

from acc.models import (AdExcelArg, AdTestType0, DeviceType, Request,
                        UserProfile)
from form.models import *
from ww.local_settings import (DL_FTP_HOST, DL_FTP_PASSWD, DL_FTP_USER,
                               dl_domain_name, domain_name)

from .models import Encode, Report

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


model_list = [MonitorSpo2_1, MonitorECG_1, MonitorNIBP_1, MonitorSafety_1, Defibrilator_1, AED_1, ECG_1,
              InfusionPump_1, SyringePump_1, Spo2_1, FlowMeter_1, AnesthesiaMachine_1, Ventilator_1,
              Suction_1, ElectroCauter_1, ManoMeter_1, CantTest, Report]
modellist = ['MonitorSpo2', 'MonitorECG', 'MonitorNIBP', 'MonitorSafety', 'Defibrilator', 'AED', 'ECG',
             'InfusionPump', 'SyringePump', 'PulseOximetry', 'FlowMeter', 'AnesthesiaMachine', 'Ventilator',
             'Suction', 'ElectroCauter', 'ManoMeter', 'CantTest']


def xlsx(request, filtering, query_start_year, query_start_month, query_start_day, query_end_year, query_end_month, query_end_day, operation_type):

    query_start_date = jdatetime.date(
        query_start_year, query_start_month, query_start_day) - timedelta(days=1)
    # because quering from data base we should consider filter data via utc time
    QUERY_START_DATE = jdatetime.datetime(
        query_start_date.year, query_start_date.month, query_start_date.day, 19, 30
    ).astimezone(pytz.timezone('UTC'))
    QUERY_END_DATE = jdatetime.datetime(
        query_end_year, query_end_month, query_end_day, 19, 30).astimezone(pytz.timezone('UTC'))
    if QUERY_END_DATE < QUERY_START_DATE:
        return render(request, 'acc/hospital/index.html', {'date_error': 'بازه زمانی وارد شده نا معتبر است',
                                                           'flag': 1})  # , 'date': jdatetime.date.today(),

    # Create Excel
    query_list = []
    chart_data = {
        'total_green': 0,
        'total_yellow': 0,
        'total_red': 0,
        'total_blue': 0,
    }

    if filtering == 'recal':
        if Group.objects.get(name='admin') in request.user.groups.all():  # admin
            # for model in model_list:
            report_query = Report.objects.filter(
                date__gte=QUERY_START_DATE).filter(
                date__lte=QUERY_END_DATE).filter(is_recal=True)
            # query_list.append(model_query)
        else:  # hospital
            # for model in model_list:
            report_query = Report.objects.filter(
                date__gte=QUERY_START_DATE).filter(
                date__lte=QUERY_END_DATE).filter(
                request__hospital__user__id__exact=request.user.id).filter(is_recal=True)
            # query_list.append(model_query)
    elif filtering == 'all':
        if Group.objects.get(name='admin') in request.user.groups.all():
            # for model in model_list:
            report_query = Report.objects.filter(
                date__gte=QUERY_START_DATE).filter(
                date__lte=QUERY_END_DATE)
            # query_list.append(model_query)
        else:  # Hospital
            # for model in model_list:
            report_query = Report.objects.filter(
                date__gte=QUERY_START_DATE).filter(
                date__lte=QUERY_END_DATE).filter(
                request__hospital__user__id__exact=request.user.id)
            # query_list.append(model_query)

    chart_data['total_green'] = len(report_query.filter(status__id=1))
    chart_data['total_yellow'] = len(report_query.filter(status__id=2))
    chart_data['total_red'] = len(report_query.filter(status__id=3))
    chart_data['total_blue'] = len(report_query.filter(status__id=4))
    # for index, query in enumerate(query_list):

    table_rows = []
    for instance in report_query:
        row = []
        row.append(instance.device.hospital.city.state.name)  # 0
        row.append(instance.device.hospital.city.name)  # 1
        row.append(instance.device.hospital.name)  # 2
        row.append(instance.device.section.name)  # 3
        row.append(instance.device.name.type.name)  # 4
        row.append(instance.device.name.creator.name)  # 5
        row.append(instance.device.name.name)  # 6
        row.append(instance.device.serial_number)  # 7
        if str(instance.device.property_number) != 'None':
            row.append(instance.device.property_number)  # 8
        else:
            row.append('-')
        row.append(instance.status.status)  # 9
        row.append(instance.date.strftime("%Y-%m-%d"))  # 10
        if instance.status.id != 4:
            row.append(instance.licence.number)  # 11
        else:
            row.append('')  # 11
        if instance.tt.type == 'MonitorSpo2':
            row.append('-SPO2-' + instance.totalcomment)  # 12*
        elif instance.tt.type == 'MonitorECG':
            row.append('-ECG-' + instance.totalcomment)  # 12*
        elif instance.tt.type == 'MonitorNIBP':
            row.append('-NIBP-' + instance.totalcomment)  # 12*
        elif instance.tt.type == 'MonitorSafety':
            row.append('-Safety-' + instance.totalcomment)  # 12*
        else:
            row.append(instance.totalcomment)  # 12*
        row.append(instance.status.id)  # 13

        encode_instance = Encode.objects.get(
            hospital=instance.device.hospital)

        row.append('https://{dl_domain}/reports/pdf/{state}/{city}/{hosp}/{req}/{section}/{device_type}/{licence}.pdf'.format(  # 14
            dl_domain=dl_domain_name,
            state=instance.device.hospital.city.state.eng_name,
            city=instance.device.hospital.city.eng_name,
            hosp=str(instance.device.hospital.user.id) + \
            '_' + encode_instance.name,
            req=instance.request.number,
            section=instance.device.section.eng_name,
            device_type=instance.tt.type,
            licence=instance.licence.number,
        )
        )
        table_rows.append(row)

    table_header_list = AdExcelArg.objects.all().order_by('id')
    table_header = (str(table_header_list[1]),
                    str(table_header_list[2]),
                    str(table_header_list[3]),
                    str(table_header_list[4]),
                    str(table_header_list[5]),
                    str(table_header_list[6]),
                    str(table_header_list[7]),
                    str(table_header_list[8]),
                    str(table_header_list[9]),
                    str(table_header_list[10]),
                    str(table_header_list[11]),
                    str(table_header_list[12]),
                    str(table_header_list[13]),
                    str(table_header_list[14]),
                    str(table_header_list[15]),
                    'PDF'
                    )

    if operation_type == 'download':

        output = io.BytesIO()
        wb = xlsxwriter.Workbook(output)
        ws = wb.add_worksheet(name='Data')
        chart_ws = wb.add_worksheet(name='Charts')

        chart_ws.right_to_left()
        ws.right_to_left()

        ws.set_default_row(height=40)
        ws.set_column(0, 15, 17)

        # first row

        table_header_format = wb.add_format({'font_size': 11, 'align': 'center',
                                             'valign': 'vcenter', 'bottom': True, 'left': True})

        ws.write_row(row=0, col=0, data=table_header,
                     cell_format=table_header_format)
        # Patterns
        green_row_format = wb.add_format(  # accept
            {'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'pattern': 1, 'bg_color': 'green',
                'bottom': True,
                'left': True})
        yellow_row_format = wb.add_format(  # conditional
            {'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'pattern': 1, 'bg_color': 'yellow',
                'bottom': True,
                'left': True})
        red_row_format = wb.add_format(  # reject
            {'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'pattern': 1, 'bg_color': 'red',
                'bottom': True,
                'left': True})
        cursor = 1

        for row in table_rows:
            # if (modelobj[i].device.hospital.user == request.user):
            # Assign Status
            if row[13] == 1:  # accept
                row_format = green_row_format
            elif row[13] == 2:  # conditional
                row_format = yellow_row_format
            elif row[13] == 3:  # conditional
                row_format = red_row_format
            else:
                row_format = table_header_format

            row_data = (cursor,
                        row[0],  # ostan
                        row[1],  # shahr
                        row[2],  # name moshtari
                        row[3],  # mahale esteqrar
                        row[4],  # mahsul
                        row[5],  # tolid konande
                        row[6],  # model
                        row[7],  # shoamre serial
                        row[8],  # kode amval
                        row[9],  # vaziate azmoon
                        row[10],  # tarikh calibration
                        str(table_header_list[0]),  # etebare calibration
                        row[11],  # shomare govahi
                        row[12],  # tozihat
                        )

            ws.write_row(row=cursor, col=0, data=row_data,
                         cell_format=row_format)

            # report_instance = Report.objects.filter(
            #     licence__number=row[11])
            # if len(report_instance):

            # Esfahan/Esfahan/a01610228fe998f515a72dd730294d87/100/AMBULANCE/AED

            ws.write_url(row=cursor, col=len(row_data), url=row[14],
                         cell_format=row_format, string='show', tip='Downlaod PDF')

            cursor += 1
        wb.close()
        output.seek(0)
        filename = f'Azma_Saba.ExcelReport.{str(jdatetime.date.today()).split()[0]}.xlsx'
        response = HttpResponse(output,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

    elif operation_type == 'show':  # display table
        # avatar_url = UserProfile.objects.get(
        #     id=1).avatar.url  # admin user_profile

        # chart = [0, 0, 0, 0]
        # if Group.objects.get(name='hospital') in request.user.groups.all():
        #     request_list = Request.objects.filter(
        #         hospital__user=request.user).order_by('date')
        #     template_name = 'acc/hospital/index.html'
        # else:
        #     request_list = Request.objects.all().order_by('date')
        #     template_name = 'acc/admin/index.html'

        # for obj in query_list:
        #     chart[0] += len(obj.filter(status__id=1))
        #     chart[1] += len(obj.filter(status__id=2))
        #     chart[2] += len(obj.filter(status__id=3))
        #     chart[3] += len(obj.filter(status__id=4))

        # for req in request_list:
        #     req.date = req.date.today()

        pass_data = {
            'table_header': table_header, 'table_rows': table_rows,
            # 'request': request_list, 'avatar_url': avatar_url,
            # 'user_name': request.user.first_name, 'chart': chart
        }
        # if Group.objects.get(name='admin') in request.user.groups.all():
        #     pass_data['admin'] = 1
        return render(request, 'acc/hospital/table.html', pass_data)


def show_request_summary(request):
    if request.method == 'GET':
        if request.GET['request'] == '1':  # get sections
            sections = []
            for model in model_list:
                temp = model.objects.filter(
                    request__number__exact=int(request.GET['req_number']))
                if len(temp) != 0:
                    for t in temp:
                        sections.append(t.device.section)
            sections = list(set(sections))  # get unique values
            for sec in sections:
                sec = sec.name

            return render(request, 'acc/employee/dlsum.html', {'data': sections, 'req_num': request.GET['req_number']})

        elif request.GET['request'] == '0':  # get report
            s = 0
            data = []
            sn = request.GET['sec_name']
            rn = int(request.GET['req_num'])
            types = DeviceType.objects.get(id__gte=13)
            for model in model_list[:-2]:
                temp = model.objects.filter(request__number__exact=rn).filter(  # number of test of each device
                    device__section__name__exact=sn)
                temp2 = CantTest.objects.filter(request__number__exact=rn).filter(  # number of cant test of each device
                    device__section__name__exact=sn).filter(tt__type__exact=AdTestType0.objects.all().order_by('id')[s/2])
                data[s] = len(temp)
                data[s+1] = len(temp2)
                s += 2

            t2 = jdatetime.datetime.today()
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = (
                'inline; '
                f'filename=summary_{sn}_{rn}.pdf'
            )
            font_config = FontConfiguration()
            # TODO add hospital infos
            html = render_to_string('report/sections_summary.html', {
                'time': t2, 'data': data
            })

            css_root = static('/css')
            css1 = CSS(filename=f'ww/{css_root}/sop2-pdf.css')
            css2 = CSS(filename=f'ww/{css_root}/bootstrap-v4.min.css')

            HTML(string=html).write_pdf(
                response, font_config=font_config, stylesheets=[css1, css2])

            return response


def reportview(request):
    if request.method == 'GET':
        if Group.objects.get(name='hospital') in request.user.groups.all():
            data = Report.objects.filter(licence__number=request.GET['licence_number']).filter(
                request__hospital__user__id__exact=request.user.id)
        else:
            data = Report.objects.filter(
                licence__number=request.GET['licence_num'])
        if len(data) != 0:
            instance = data[0] 
            encode_instance = Encode.objects.get(
                hospital=instance.device.hospital)
            return redirect('https://{dl_domain}/reports/pdf/{state}/{city}/{hosp}/{req}/{section}/{device_type}/{licence}.pdf'.format(  # 14
                dl_domain=dl_domain_name,
                state=instance.device.hospital.city.state.eng_name,
                city=instance.device.hospital.city.eng_name,
                hosp=str(instance.device.hospital.user.id) + \
                '_' + encode_instance.name,
                req=instance.request.number,
                section=instance.device.section.eng_name,
                device_type=instance.tt.type,
                licence=instance.licence.number,

            ))

        raise Http404
    else:
        raise Http404
