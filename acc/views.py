import jdatetime
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.shortcuts import Http404, redirect, render


from acc.models import Parameters, Request, AdExcelArg
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
#              ManoMeter_1_Form, spo2_1_Form, suction_1_Form, syringe_pump_1_Form, ventilator_1_Form, electrocauter_1_Form,
#              CantTest_Form]

model_list = [['MonitorSpo2', MonitorSpo2_1, MonitorSpo2_1_Form],
              ['MonitorECG', MonitorECG_1, MonitorECG_1_Form],
              ['MonitorNIBP', MonitorNIBP_1, MonitorNIBP_1_Form],
              ['MonitorSafety', MonitorSafety_1, MonitorSafety_1_Form],
              ['Defibrilator', Defibrilator_1, Defibrilator_1_Form],
              ['AED', AED_1, AED_1_Form],
              ['ECG', ECG_1, ECG_1_Form],
              ['InfusionPump', InfusionPump_1, InfusionPump_1_Form],
              ['SyringePump', SyringePump_1, syringe_pump_1_Form],
              ['spo2', Spo2_1, spo2_1_Form],
              ['FlowMeter', FlowMeter_1, FlowMeter_1_Form],
              ['AnesthesiaMachine', AnesthesiaMachine_1,
               AnesthesiaMachine_1_Form],
              ['Ventilator', Ventilator_1, ventilator_1_Form],
              ['Suction', Suction_1, suction_1_Form],
              ['ManoMeter', ManoMeter_1, ManoMeter_1_Form],
              ['Incubator', ManoMeter_1, ManoMeter_1_Form],
              ['ElectroCauter', ElectroCauter_1, electrocauter_1_Form],
              ['CantTest', CantTest, CantTest_Form],
              ['Report', Report],  
              ]  # Order the same by AdTestType0


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
    id = models.IntegerField(primary_key=True)
    avatar_url = UserProfile.objects.all()[0].avatar.url  # admin user_profile
    if Group.objects.get(name='admin') in request.user.groups.all():
        try:
            request.GET['employee']  # if the admin asked for user_dashboard
            return render(request, 'acc/employee/index.html', {'status1': 'خوش آمدید', 'user_name': request.user.first_name, 'avatar_url': avatar_url})
        except:
            # hospital_list = Hospital.objects.all()
            request_list = Request.objects.all().order_by('date')
            chart = [0, 0, 0, 0]
            # [accept, conditional, reject, cant test]
            for model in model_list:
                if model[1] == CantTest:
                    continue
                chart[0] += len(model[1].objects.filter(status__id=1))
                chart[1] += len(model[1].objects.filter(status__id=2))
                chart[2] += len(model[1].objects.filter(status__id=3))
            chart[3] = len(CantTest.objects.all())
            for req in request_list:
                req.date = req.date.today()

            return render(request, 'acc/admin/index.html', {
                'status': 'Welcome Back', 'user_name': request.user.first_name, 'request_list': request_list,
                'chart': chart, 'avatar_url': avatar_url})

    elif Group.objects.get(name='hospital') in request.user.groups.all():

        request_list = Request.objects.filter(
            hospital__user=request.user).order_by('date')
        chart = [0, 0, 0, 0]
        # [accept, conditional, reject, cant test]
        for model in model_list:
            if model[1] == CantTest:
                continue
            query = model[1].objects.filter(
                device__hospital__user=request.user)

            chart[0] += len(query.filter(status__id=1))
            chart[1] += len(query.filter(status__id=2))
            chart[2] += len(query.filter(status__id=3))
        chart[3] = len(CantTest.objects.filter(
            device__hospital__user=request.user))
        for req in request_list:
            req.date = req.date.today()
        return render(request, 'acc/hospital/index.html',
                      {'status': 'خوش آمدید', 'request_list': request_list, 'avatar_url': avatar_url,
                       'user_name': request.user.first_name, 'chart': chart})
        #    'date': jdatetime.date.today(), 'month': mm,

    elif Group.objects.get(name='employee') in request.user.groups.all():
        return render(request, 'acc/employee/index.html', {'status1': 'خوش آمدید',
                                                           'avatar_url': avatar_url, 'user_name': request.user.first_name})


# list of requests
def show_request_list(request):
    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(name='employee') in request.user.groups.all():
        request_list = Request.objects.all()
        for req in request_list:
            req.date = jdatetime.date.fromgregorian(date=req.date)
        return render(request, 'acc/employee/request_list.html', {'request_list': request_list})
    else:
        raise Http404

# List of recalibration


def show_recalibration_list(request):
    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(name='employee') in request.user.groups.all():
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
        for model in model_list:
            model_query = model[1].objects.filter(is_done=False)
        #     model_query_list.append(model_query)
        # for model_ in model_query_list:
            for obj in model_query:
                # obj = report_instance
                row = []
                row.append(obj.device.hospital.city.state.name)  # 0
                row.append(obj.device.hospital.city.name)  # 1
                row.append(obj.device.hospital.name)  # 2
                row.append(obj.device.section.name)  # 3
                row.append(obj.device.name.type.name)  # 4
                row.append(obj.device.name.creator.name)  # 5
                row.append(obj.device.name.name)  # 6
                row.append(obj.device.serial_number)  # 7
                row.append(obj.device.property_number)  # 8
                row.append(obj.status.status)  # 9
                row.append(obj.date.strftime("%Y-%m-%d"))  # 10
                if obj.status.id != 4:
                    row.append(obj.licence.number)  # 11
                else:
                    row.append('-')  # 11
                row.append(obj.record.number)  # 12
                row.append(obj.totalcomment)  # 13
                table_rows.append(row)

        return render(request, 'acc/employee/recalibration_list.html', {'table_header': table_header, 'table_rows': table_rows})
    else:
        raise Http404

# list of all records


def show_report_list(request):
    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(name='employee') in request.user.groups.all():
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
        # data1 = []
        # for model in model_list[:-1]:
        model_query = model_list[-1][1].objects.all()
        #     data1.append(modelobj)
        # for obj1 in data1:
        for obj in model_query:
            row = []
            row.append(obj.device.hospital.city.state.name)  # 0
            row.append(obj.device.hospital.city.name)  # 1
            row.append(obj.device.hospital.name)  # 2
            row.append(obj.device.section.name)  # 3
            row.append(obj.device.name.type.name)  # 4
            row.append(obj.device.name.creator.name)  # 5
            row.append(obj.device.name.name)  # 6
            row.append(obj.device.serial_number)  # 7
            row.append(obj.device.property_number)  # 8
            row.append(obj.status.status)  # 9
            row.append(obj.date.strftime("%Y-%m-%d"))  # 10
            if obj.status.id != 4:
                row.append(obj.licence.number)  # 11
            else:
                row.append('-')  # 11
            row.append(obj.record.number)  # 12
            row.append(obj.totalcomment)  # 13
            table_rows.append(row)
        return render(request, 'acc/employee/report_list.html', {'table_header': table_header, 'table_rows': table_rows})
    else:
        raise Http404

# Perepare the appropiate Edit form for Frame


def edit_report(request):
    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(name='employee') in request.user.groups.all():
        if (request.method == 'GET'):
            avatar_url = UserProfile.objects.get(
                id=1).avatar.url  # admin user_profile
            try:
                for model in model_list:
                    model_query = model[1].objects.filter(
                        record__number=int(request.GET['record_number']))
                    if (len(model_query) == 1):
                        form_type = model[2]
                        model_name = model[0]
                        break
            except:
                # return redirect('dashboard')
                pass
            # try:
            #     form_type
            # except:
            #     raise Http404
            form_body = form_type(instance=model_query[0])
            pass_data = {'form': form_body,
                         'form_type': model_name,
                         'record_number': model_query[0].record.number,
                         'licence_number': model_query[0].licence.number,
                         'user_name': request.user.first_name, 'avatar_url': avatar_url
                         }

            if (model_query[0].is_recal == False):  # its calibration
                pass_data['edit'] = 1
            else:
                pass_data['edit_recal'] = 1
            return render(request, 'acc/employee/index.html', pass_data)
        else:
            return('report_list')
    else:
        raise Http404

# Perepare the appropiate Recalibration form for Frame


def recal_report(request):
    if Group.objects.get(name='admin') in request.user.groups.all() or Group.objects.get(name='employee') in request.user.groups.all():
        if (request.method == 'GET'):
            avatar_url = UserProfile.objects.get(
                id=1).avatar.url  # admin user_profile
            for model in model_list:
                model_query = model[1].objects.filter(record__number=int(request.GET['record_number'])).filter(
                    is_done__exact=False)

                if (len(model_query) == 1):
                    if model[0] in ['CantTest', 'report']:
                        form_type = model_list[int(model_query[0].tt.id)-1][2]
                        model_name = model_list[int(model_query[0].tt.id)-1][0]
                    else:
                        form_type = model[2]
                        model_name = model[0]
                    break
                # else:
                #     return('recal_list')

            # form_body = form_type({'device': [model_query[0].device.id]})
            form_body = form_type
            pass_data = {'recal': 1,
                         'form': form_body,
                         'form_type': model_name,
                         'ref_record_number': model_query[0].record.number,
                         'user_name': request.user.first_name, 'avatar_url': avatar_url
                         }
            try:
                # if exist
                pass_data['ref_licence_num'] = model_query[0].licence.number
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
    if (request.method == 'POST'):
        if (request.POST['email1'] == request.POST['email2']):
            d = User.objects.get(id=request.user.id)
            d.email = request.POST['email1']
            d.save()
            return render(request, 'registration/email_change_done.html')
        else:
            return render(request, 'registration/email_change_form.html',
                          {'red_status': 'ایمیل ها مطابقت ندارند!'})
    else:
        return render(request, 'registration/email_change_form.html')
