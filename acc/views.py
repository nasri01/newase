import jdatetime
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import Http404, redirect, render, HttpResponse

# from acc.models import Parameters, Request, AdExcelArg
from form.forms import *
from report.models import Report
from .forms import *

try:
    color_scheme = Parameters.objects.get(name__exact='color').value
except:
    color_scheme = '17a2b8'
# model_list = [MonitorSpo2_1, MonitorECG_1, MonitorNIBP_1, MonitorSafety_1, AED_1, AnesthesiaMachine_1,
#               Defibrilator_1, ECG_1, FlowMeter_1, InfusionPump_1, ManoMeter_1, Spo2_1, Suction_1, SyringePump_1,
#               Ventilator_1, ElectroCauter_1, CantTest, report]

# modellist = ['MonitorSpo2', 'MonitorECG', 'MonitorNIBP', 'MonitorSafety', 'AED', 'AnesthesiaMachine',
#              'Defibrilator', 'ECG', 'FlowMeter', 'InfusionPump', 'ManoMeter', 'spo2', 'Suction', 'SyringePump',
#              'Ventilator', 'ElectroCauter', 'CantTest']

# form_list = [MonitorSpo2_1_Form, MonitorECG_1_Form, MonitorNIBP_1_Form, MonitorSafety_1_Form, AED_1_Form,
#              AnesthesiaMachine_1_Form, Defibrilator_1_Form, ECG_1_Form, FlowMeter_1_Form, InfusionPump_1_Form,
#              ManoMeter_1_Form, spo2_1_Form, Suction_1_Form, Syringe_pump_1_Form, Ventilator_1_Form, ElectroCauter_1_Form,
#              CantTest_Form]

model_dict = {'MonitorSpo2': [[MonitorSpo2_1, MonitorSpo2_1_Form, 3]],
              'MonitorECG': [[MonitorECG_1, MonitorECG_1_Form, 3]],
              'MonitorNIBP': [[MonitorNIBP_1, MonitorNIBP_1_Form, 3]],
              'MonitorSafety': [[MonitorSafety_1, MonitorSafety_1_Form, 3]],
              'Defibrilator': [[Defibrilator_1, Defibrilator_1_Form, 4]],
              'AED': [[AED_1, AED_1_Form, 2]],
              'ECG': [[ECG_1, ECG_1_Form, 4]],
              'InfusionPump': [[InfusionPump_1, InfusionPump_1_Form, 4]],
              'SyringePump': [[SyringePump_1, Syringe_pump_1_Form, 4]],
              'spo2': [[Spo2_1, spo2_1_Form, 4]],
              'FlowMeter': [[FlowMeter_1, FlowMeter_1_Form, 1]],
              'AnesthesiaMachine': [[AnesthesiaMachine_1, AnesthesiaMachine_1_Form, 4]],
              'Ventilator': [[Ventilator_1, Ventilator_1_Form, 4]],
              'Suction': [[Suction_1, Suction_1_Form, 4]],
              'ManoMeter': [[ManoMeter_1, ManoMeter_1_Form, 3]],
              # 'AutoClave': [[AutoClave_1, AutoClave_1]], #TODO AutoClave form
              'ElectroCauter': [[ElectroCauter_1, ElectroCauter_1_Form, 5]],
            #   'CantTest': [[CantTest, CantTest_Form]],
            #   'Report': [[Report]],
              }  # Order the same by AdTestType0


def login(request):
    if request.method == 'POST':
        user = auth.authenticate(
            username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            auth.login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'acc/login.html',
                          {'error': 'نام کاربری یا رمز عبور اشتباه است!', 'color': color_scheme})
    elif request.user.is_anonymous:
        return render(request, 'acc/login.html', {'color': color_scheme})
    else:
        return redirect('dashboard')


def logout(request):
    auth.logout(request)
    return redirect('login1')


@login_required
def route_to_dashboard(request):
    avatar_url = UserProfile.objects.all()[0].avatar.url  # admin user_profile
    if Group.objects.get(name='admin') in request.user.groups.all():
        try:
            request.GET['employee']  # if the admin asked for user_dashboard
            return render(request, 'acc/employee/index.html',
                          {'user_name': request.user.first_name, 'avatar_url': avatar_url})
        except:
            hospital_list = Hospital.objects.all()
            hospital_dict = {}
            for hospital in hospital_list:
                hospital_dict['{}'.format(hospital.id)] = hospital.name
            request_list = Request.objects.all().order_by('-date')
            chart = [0, 0, 0, 0]
            
            # [accept, conditional, reject, cant test]
            # for model in model_list:
            #     if model[1] == CantTest:
            #         continue
            #     chart[0] += len(model[1].objects.filter(status__id=1))
            #     chart[1] += len(model[1].objects.filter(status__id=2))
            #     chart[2] += len(model[1].objects.filter(status__id=3))
            # chart[3] = len(CantTest.objects.all())
            # for req in request_list:
            #     req.date = req.date.today()

            return render(request, 'acc/admin/index.html', {
                'user_name': request.user.first_name, 'request_list': request_list,
                'chart': chart, 'avatar_url': avatar_url, 'hospital_dict': hospital_dict})

    elif Group.objects.get(name='hospital') in request.user.groups.all():

        request_list = Request.objects.filter(
            hospital__user=request.user).order_by('date')
        chart = [0, 0, 0, 0]

        # [accept, conditional, reject, cant test]
        # for model in model_list:
        #     if model[1] == CantTest:
        #         continue
        #     query = model[1].objects.filter(
        #         device__hospital__user=request.user)

        #     chart[0] += len(query.filter(status__id=1))
        #     chart[1] += len(query.filter(status__id=2))
        #     chart[2] += len(query.filter(status__id=3))
        # chart[3] = len(CantTest.objects.filter(
        #     device__hospital__user=request.user))
        # for req in request_list:
        #     req.date = req.date.today()
        return render(request, 'acc/hospital/index.html',
                      {'request_list': request_list, 'avatar_url': avatar_url,
                       'user_name': request.user.first_name, 'chart': chart})
        #    'date': jdatetime.date.today(), 'month': mm,

    elif Group.objects.get(name='employee') in request.user.groups.all():
        return render(request, 'acc/employee/index.html', {'status1': 'خوش آمدید',
                                                           'avatar_url': avatar_url,
                                                           'user_name': request.user.first_name})


# list of requests
def show_request_list(request):
    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(
            name='employee') in request.user.groups.all():
        request_list = Request.objects.all()
        for req in request_list:
            req.date = jdatetime.date.fromgregorian(date=req.date)
        return render(request, 'acc/employee/request_list.html', {'request_list': request_list})
    else:
        raise Http404


# List of recalibration
def show_recalibration_list(request):
    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(
            name='employee') in request.user.groups.all():
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
                        )
        table_rows = []
        # model_query_list = []
        for t, model_hist in model_dict.items():
            if t == 'Report':
                continue
            for model in model_hist:
                model_query = model[0].objects.filter(is_done=False)
                for obj in model_query:
                    row = {}
                    row['test_model_name'] = model_query.model.__name__  # for reffrence when clicko=ing on edit ad delete button
                    row['state_name'] = obj.device.hospital.city.state.name
                    row['city_name'] = obj.device.hospital.city.name
                    row['hospital_name'] = obj.device.hospital.name
                    row['section_name'] = obj.device.section.name
                    row['device_type_name'] = obj.device.name.type.name
                    row['device_creator_name'] = obj.device.name.creator.name
                    row['device_name'] = obj.device.name.name
                    row['device_serial_number'] = obj.device.serial_number
                    row['device_property_number'] = obj.device.property_number
                    row['test_status'] = obj.status.status
                    row['test_time'] = obj.date.strftime("%Y-%m-%d")

                    if obj.status.id != 4:
                        row['test_licence_number'] = obj.licence.number
                    else:
                        row['test_licence_number'] = '-'
                    row['test_record_number'] = obj.record.number
                    # row.append(obj.totalcomment) 
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

                    table_rows.append(row)

        return render(request, 'acc/employee/recalibration_list.html',
                      {'table_header': table_header, 'table_rows': table_rows})
    else:
        raise Http404


# list of all records
def show_report_list(request, select_hospital):
    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(
            name='employee') in request.user.groups.all():
        if int(select_hospital) == 1:
            hospital_list = Hospital.objects.all().values('id', 'name', 'city')
            return render(request, 'acc/employee/report_list_select_hospital.html', {'hospital_list': hospital_list})
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
                        )
        table_rows = []
        # model_query = model_dict['Report'][1].objects.filter(device__hospital__id=request.POST['hospital'])
        for t, model_hist in model_dict.items():
            if t == 'Report':
                continue
            for model in reversed(model_hist):
                model_query = model[0].objects.filter(device__hospital__id=request.POST['hospital'])
                for obj in model_query:
                    row = {}
                    row['test_model_name'] = model_query.model.__name__
                    row['state_name'] = obj.device.hospital.city.state.name
                    row['city_name'] = obj.device.hospital.city.name
                    row['hospital_name'] = obj.device.hospital.name
                    row['section_name'] = obj.device.section.name
                    row['device_type_name'] = obj.device.name.type.name
                    row['device_creator_name'] = obj.device.name.creator.name
                    row['device_name'] = obj.device.name.name
                    row['device_serial_number'] = obj.device.serial_number
                    row['device_property_number'] = obj.device.property_number
                    row['test_status'] = obj.status.status
                    row['test_time'] = obj.date.strftime("%Y-%m-%d")
                    if obj.status.id != 4:
                        row['test_licence_number'] = obj.licence.number
                    else:
                        row['test_licence_number'] = '-'
                    row['test_record_number'] = obj.record.number
                    # row.append(obj.totalcomment) 
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
                    table_rows.append(row)

        return render(request, 'acc/employee/report_list.html',
                      {'table_header': table_header, 'table_rows': table_rows})
    else:
        raise Http404


# Perepare the appropiate Edit form for Frame
def edit_report(request):
    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(
            name='employee') in request.user.groups.all():
        if request.method == 'GET':
            avatar_url = UserProfile.objects.get(
                id=1).avatar.url  # admin user_profile
            try:
                model_name = request.GET['test_model_name'].split('_')[0]
                model_hist = model_dict[model_name]

                for model in model_hist:
                    model_query = model[0].objects.filter(
                        record__number=int(request.GET['test_record_number']))
                    if len(model_query) == 1:
                        form_type = model[1]
                        break
            except:
                # return redirect('dashboard')
                return Http404
            form_body = form_type(instance=model_query[0])
            pass_data = {'form': form_body,
                         'form_type': model_name,
                         'test_record_number': request.GET['test_record_number'],
                         'test_licence_number': model_query[0].licence.number,
                         'user_name': request.user.first_name, 'avatar_url': avatar_url,
                         'test_form_type': model_name
                         }

            if (model_query[0].is_recal == False):  # its not calibration
                pass_data['edit'] = 1
            else:
                pass_data['edit_recal'] = 1
            return render(request, 'acc/employee/index.html', pass_data)
        else:
            return ('report_list')
    else:
        raise Http404


# Perepare the appropiate Recalibration form for Frame
def recal_report(request):
    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(
            name='employee') in request.user.groups.all():
        if request.method == 'GET':
            avatar_url = UserProfile.objects.get(
                id=1).avatar.url  # admin user_profile

            model_name = request.GET['test_model_name'].split('_')[0]
            model_hist = model_dict[model_name]
            for model in model_hist:
                q_exclude_field = model[1].Meta.exclude  # List of excluded Filed
                model_query = model[0].objects.filter(
                    record__number=int(request.GET['test_record_number'])).filter(
                    is_done__exact=False)

                if len(model_query) == 1:
                    break

            if model_name in ['CantTest', 'report']:
                form_type = model_dict[model_query[0].tt][-1][1]  # get last appropiate version form object

            else:
                form_type = model[1]

            q_dict = model_query.values()[0]  # get the data as dictionary

            q_d = {}
            for k in q_dict:
                q_d[k.replace('_id', '')] = q_dict[k]
            del q_dict
            q_exclude_field.append('id')
            for field in q_exclude_field:
                q_d.pop(field)
            # form_body = form_type({'device': [model_query[0].device.id]})
            form_body = form_type(initial=q_d)

            pass_data = {'recal': 1,
                         'form': form_body,
                         'test_form_type': model_name,
                         'test_ref_record_number': model_query[0].record.number,
                         'user_name': request.user.first_name, 'avatar_url': avatar_url
                         }
            try:
                # if exist
                pass_data['test_ref_licence_number'] = model_query[0].licence.number
            except:
                pass
            return render(request, 'acc/employee/index.html', pass_data)
    else:
        raise Http404


def make_done(request):
    if (request.method == 'GET'):
        query = CantTest.objects.filter(
            record__number=int(request.GET['record_number']))
        query[0].is_done = True
        query[0].save()

        return redirect('recal_list')
    else:
        raise Http404


@login_required
def change_email(request):
    if request.method == 'POST':
        if request.POST['email1'] == request.POST['email2']:
            d = User.objects.get(id=request.user.id)
            d.email = request.POST['email1']
            d.save()
            return render(request, 'registration/email_change_done.html')
        else:
            return render(request, 'registration/email_change_form.html',
                          {'red_status': 'ایمیل ها مطابقت ندارند!'})
    else:
        return render(request, 'registration/email_change_form.html')


def add_what(request, what):
    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(
            name='employee') in request.user.groups.all():
        if request.method == 'POST':  # Save the Device
            sform = add_device_Form(request.POST)
            if not sform.is_valid():
                return HttpResponse('فرم ناقص')
            sform.save()
            return HttpResponse('saved!')
        else:  # Show the Form
            data = {}
            if what == 'device':
                form = add_device_Form()
                data['form'] = form
                data['formTitle1'] = 'افزودن دستگاه'
                data['field1Name'] = 'مدل دستگاه'
                data['field2Name'] = 'نام بیمارستان'
                data['field3Name'] = 'نام بخش'
                data['formTitle2'] = 'مشخصات دستگاه'
                data['field4Name'] = 'شماره اموال'
                data['field5Name'] = 'سریال دستگاه'
                return render(request, 'acc/employee/add_what.html', data)
    else:
        return Http404
