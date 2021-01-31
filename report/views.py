import io
import os

import jdatetime
import pytz
import xlsxwriter
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.shortcuts import Http404, redirect, render
from django.template.loader import render_to_string
from django.templatetags import static
from jdatetime import timedelta
from weasyprint import CSS, HTML
from weasyprint.fonts import FontConfiguration

from acc.models import AdExcelArg, AdTestType0, DeviceType
from form.models import *
from ww.local_settings import dl_domain_name
from .models import Encode, Report
from acc.views import model_dict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# model_list = [MonitorSpo2_1, MonitorECG_1, MonitorNIBP_1, MonitorSafety_1, Defibrilator_1, AED_1, ECG_1,
#               InfusionPump_1, SyringePump_1, Spo2_1, FlowMeter_1, AnesthesiaMachine_1, Ventilator_1,
#               Suction_1, ElectroCauter_1, ManoMeter_1, CantTest, Report]


def xlsx(request, filtering, query_start_year, query_start_month, query_start_day, query_end_year, query_end_month,
         query_end_day, operation_type):
    """

    Args:
        request:
        filtering:
        query_start_year:
        query_start_month:
        query_start_day:
        query_end_year:
        query_end_month:
        query_end_day:
        operation_type:

    Returns:

    """
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

    # chart_data = {
    #     'total_green': 0,
    #     'total_yellow': 0,
    #     'total_red': 0,
    #     'total_blue': 0,
    # }

    table_rows = []
    for t, model_hist in model_dict.items():
        if t == 'Report':
            continue
        for model in model_hist:
            report_query = model[0].objects.filter(
                date__gte=QUERY_START_DATE).filter(
                date__lte=QUERY_END_DATE)
            if Group.objects.get(name='hospital') in request.user.groups.all():  # admin
                report_query = report_query.filter(
                    request__hospital__user__id__exact=request.user.id)
            if filtering == 'recal':
                report_query = report_query.filter(
                    is_recal=True)
            for obj in report_query:
                row = {'state_name': obj.device.hospital.city.state.name, 'city_name': obj.device.hospital.city.name,
                       'hospital_name': obj.device.hospital.name, 'section_name': obj.device.section.name,
                       'device_type_name': obj.device.name.type.name,
                       'device_creator_name': obj.device.name.creator.name, 'device_name': obj.device.name.name,
                       'device_serial_number': obj.device.serial_number}
                if str(obj.device.property_number) != 'None':
                    row['device_property_number'] = obj.device.property_number
                else:
                    row['device_property_number'] = '-'
                row['test_status'] = obj.status.status
                row['test_time'] = obj.date.strftime("%Y-%m-%d")
                if obj.status.id != 4:
                    row['test_licence_number'] = obj.licence.number
                else:
                    row['test_licence_number'] = '-'
                if t == 'MonitorSpo2':
                    row['test_comment'] = '-SPO2-' + obj.totalcomment
                elif t == 'MonitorECG':
                    row['test_comment'] = '-ECG-' + obj.totalcomment
                elif t == 'MonitorNIBP':
                    row['test_comment'] = '-NIBP-' + obj.totalcomment
                elif t == 'MonitorSafety':
                    row['test_comment'] = '-Safety-' + obj.totalcomment
                else:
                    row['test_comment'] = obj.totalcomment

                row['test_status_id'] = obj.status.id  # dor excel row color

                encode_obj = Encode.objects.get(
                    hospital=obj.device.hospital)

                row['url'] = 'https://{dl_domain}/reports/pdf/{state}/{city}/{hosp}/{req}/'
                '{section}/{device_type}/{licence}.pdf'.format(
                    dl_domain=dl_domain_name,
                    state=obj.device.hospital.city.state.eng_name,
                    city=obj.device.hospital.city.eng_name,
                    hosp=str(obj.device.hospital.user.id) + '_' + encode_obj.name,
                    req=obj.request.number,
                    section=obj.device.section.eng_name,
                    device_type=t,
                    licence=obj.licence.number,
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

    # chart_data['total_green'] = len(report_query.filter(status__id=1))
    # chart_data['total_yellow'] = len(report_query.filter(status__id=2))
    # chart_data['total_red'] = len(report_query.filter(status__id=3))
    # chart_data['total_blue'] = len(report_query.filter(status__id=4))
    # for index, query in enumerate(query_list):

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
            if row['test_status_id'] == 1:  # accept
                row_format = green_row_format
            elif row['test_status_id'] == 2:  # conditional
                row_format = yellow_row_format
            elif row['test_status_id'] == 3:  # conditional
                row_format = red_row_format
            else:
                row_format = table_header_format

            row_data = (cursor,
                        row['state_name'],  # ostan
                        row['city_name'],  # shahr
                        row['hospital_name'],  # name moshtari
                        row['section_name'],  # mahale esteqrar
                        row['device_type_name'],  # mahsul
                        row['device_creator_name'],  # tolid konande
                        row['device_name'],  # model
                        row['device_serial_number'],  # shoamre serial
                        row['device_property_number'],  # kode amval
                        row['test_status'],  # vaziate azmoon
                        row['test_time'],  # tarikh calibration
                        str(table_header_list[0]),  # etebare calibration
                        row['test_licence_number'],  # shomare govahi
                        row['test_comment'],  # tozihat
                        )
            ws.write_row(row=cursor, col=0, data=row_data,
                         cell_format=row_format)
            ws.write_url(row=cursor, col=len(row_data), url=row['url'],
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
        if Group.objects.get(name='admin') in request.user.groups.all():
            pass_data['admin'] = 1
        return render(request, 'acc/hospital/table.html', pass_data)


def show_request_summary(request):
    # if request.method == 'GET':
    #     if request.GET['request'] == '1':  # get sections
    #         sections = []
    #         for model in model_list:
    #             temp = model.objects.filter(
    #                 request__number__exact=int(request.GET['req_number']))
    #             if len(temp) != 0:
    #                 for t in temp:
    #                     sections.append(t.device.section)
    #         sections = list(set(sections))  # get unique values
    #         for sec in sections:
    #             sec = sec.name

    #         return render(request, 'acc/employee/dlsum.html', {'data': sections, 'req_num': request.GET['req_number']})

    #     elif request.GET['request'] == '0':  # get report
    #         s = 0
    #         data = []
    #         sn = request.GET['sec_name']
    #         rn = int(request.GET['req_num'])
    #         types = DeviceType.objects.get(id__gte=13)
    #         for model in model_list[:-2]:
    #             temp = model.objects.filter(request__number__exact=rn).filter(  # number of test of each device
    #                 device__section__name__exact=sn)
    #             temp2 = CantTest.objects.filter(request__number__exact=rn).filter(  # number of cant test of each device
    #                 device__section__name__exact=sn).filter(
    #                 tt__type__exact=AdTestType0.objects.all().order_by('id')[s / 2])
    #             data[s] = len(temp)
    #             data[s + 1] = len(temp2)
    #             s += 2

    #         t2 = jdatetime.datetime.today()
    #         response = HttpResponse(content_type='application/pdf')
    #         response['Content-Disposition'] = (
    #             'inline; '
    #             f'filename=summary_{sn}_{rn}.pdf'
    #         )
    #         font_config = FontConfiguration()
    #         # TODO add hospital infos
    #         html = render_to_string('report/sections_summary.html', {
    #             'time': t2, 'data': data
    #         })

    #         css_root = static('/css')
    #         css1 = CSS(filename=f'ww/{css_root}/sop2-pdf.css')
    #         css2 = CSS(filename=f'ww/{css_root}/bootstrap-v4.min.css')

    #         HTML(string=html).write_pdf(
    #             response, font_config=font_config, stylesheets=[css1, css2])

            return response


def reportview(request):
    if request.method == 'GET':
        for t, model_hist in model_dict.items():
            if t == 'Report':
                continue
            for model in reversed(model_hist):
                data = model[0].objects.filter(
                    licence__number=request.GET['test_licence_number'])
                if len(data) != 0:
                    if Group.objects.get(name='hospital') in request.user.groups.all():
                        data = data.filter(request__hospital__user__exact=request.user)
                    instance = data[0]
                    encode_instance = Encode.objects.get(hospital=instance.device.hospital)
                    return redirect(
                        'https://{dl_domain}/reports/pdf/{state}/{city}/{hosp}/{req}/{section}/{device_type}/{'
                        'licence}.pdf'.format(
                            dl_domain=dl_domain_name,
                            state=instance.device.hospital.city.state.eng_name,
                            city=instance.device.hospital.city.eng_name,
                            hosp=str(instance.device.hospital.user.id) + '_' + encode_instance.name,
                            req=instance.request.number,
                            section=instance.device.section.eng_name,
                            device_type=instance.tt.type,
                            licence=instance.licence.number,
                        ))
        raise Http404
    else:
        raise Http404
