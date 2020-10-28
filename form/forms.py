from django import forms
from acc.models import AllDevice
from .models import *


class CantTest_Form(forms.ModelForm):
    class Meta:
        model = CantTest
        #fields = '__all__'
        exclude = ['record', 'user', 'date', 'is_done']


class MonitorSpo2_1_Form(forms.ModelForm):
    class Meta:
        model = MonitorSpo2_1
        #fields = '__all__'
        exclude = ['is_done', 'is_recal', 'has_pdf',  'ref_record', 'record', 'user', 'date', 'licence',
                   'cal_dev_1_cd', 'cal_dev_1_xd', 'cal_dev_2_cd', 'cal_dev_2_xd', 'cal_dev_3_cd', 'cal_dev_3_xd']


class MonitorECG_1_Form(forms.ModelForm):
    class Meta:
        model = MonitorECG_1
        #fields = '__all__'
        exclude = ['is_done', 'is_recal', 'has_pdf',  'ref_record', 'record', 'user', 'date', 'licence',
                   'cal_dev_1_cd', 'cal_dev_1_xd', 'cal_dev_2_cd', 'cal_dev_2_xd', 'cal_dev_3_cd', 'cal_dev_3_xd']


class MonitorNIBP_1_Form(forms.ModelForm):
    class Meta:
        model = MonitorNIBP_1
        #fields = '__all__'
        exclude = ['is_done', 'is_recal', 'has_pdf',  'ref_record', 'record', 'user', 'date', 'licence',
                   'cal_dev_1_cd', 'cal_dev_1_xd', 'cal_dev_2_cd', 'cal_dev_2_xd', 'cal_dev_3_cd', 'cal_dev_3_xd']


class AED_1_Form(forms.ModelForm):
    class Meta:
        model = AED_1
        #fields = '__all__'
        exclude = ['is_done', 'is_recal', 'has_pdf',  'ref_record', 'record', 'user', 'date',
                   'licence', 'cal_dev_1_cd', 'cal_dev_1_xd', 'cal_dev_2_cd', 'cal_dev_2_xd']


class MonitorSafety_1_Form(forms.ModelForm):
    class Meta:
        model = MonitorSafety_1
        #fields = '__all__'
        exclude = ['is_done', 'is_recal', 'has_pdf',  'ref_record', 'record', 'user', 'date', 'licence', 'cal_dev_1_cd',
                   'cal_dev_1_xd', 'cal_dev_2_cd', 'cal_dev_2_xd', 'cal_dev_3_cd', 'cal_dev_3_xd']


class AnesthesiaMachine_1_Form(forms.ModelForm):
    class Meta:
        model = AnesthesiaMachine_1
        #fields = '__all__'
        exclude = ['is_done', 'is_recal', 'has_pdf',  'ref_record', 'record', 'user', 'date', 'licence', 'cal_dev_1_cd',
                   'cal_dev_1_xd', 'cal_dev_2_cd', 'cal_dev_2_xd', 'cal_dev_3_cd', 'cal_dev_3_xd', 'cal_dev_4_cd', 'cal_dev_4_xd']


class Defibrilator_1_Form(forms.ModelForm):
    class Meta:
        model = Defibrilator_1
        #fields = '__all__'
        exclude = ['is_done', 'is_recal', 'has_pdf',  'ref_record', 'record', 'user', 'date', 'licence', 'cal_dev_1_cd',
                   'cal_dev_1_xd', 'cal_dev_2_cd', 'cal_dev_2_xd', 'cal_dev_3_cd', 'cal_dev_3_xd', 'cal_dev_4_cd', 'cal_dev_4_xd']


class ECG_1_Form(forms.ModelForm):
    class Meta:
        model = ECG_1
        #fields = '__all__'
        exclude = ['is_done', 'is_recal', 'has_pdf',  'ref_record', 'record', 'user', 'date', 'licence', 'cal_dev_1_cd',
                   'cal_dev_1_xd', 'cal_dev_2_cd', 'cal_dev_2_xd', 'cal_dev_3_cd', 'cal_dev_3_xd', 'cal_dev_4_cd', 'cal_dev_4_xd']


class FlowMeter_1_Form(forms.ModelForm):
    class Meta:
        model = FlowMeter_1
        #fields = '__all__'
        exclude = ['is_done', 'is_recal', 'has_pdf',  'ref_record', 'record',
                   'user', 'date', 'licence', 'cal_dev_1_cd', 'cal_dev_1_xd']


class InfusionPump_1_Form(forms.ModelForm):
    class Meta:
        model = InfusionPump_1
        #fields = '__all__'
        exclude = ['is_done', 'is_recal', 'has_pdf',  'ref_record', 'record', 'user', 'date', 'licence', 'cal_dev_1_cd',
                   'cal_dev_1_xd', 'cal_dev_2_cd', 'cal_dev_2_xd', 'cal_dev_3_cd', 'cal_dev_3_xd', 'cal_dev_4_cd', 'cal_dev_4_xd']


class ManoMeter_1_Form(forms.ModelForm):
    class Meta:
        model = ManoMeter_1
        #fields = '__all__'
        exclude = ['is_done', 'is_recal', 'has_pdf',  'ref_record', 'record', 'user', 'date', 'licence',
                   'cal_dev_1_cd', 'cal_dev_1_xd', 'cal_dev_2_cd', 'cal_dev_2_xd', 'cal_dev_3_cd', 'cal_dev_3_xd']


class spo2_1_Form(forms.ModelForm):
    class Meta:
        model = Spo2_1
        #fields = '__all__'
        exclude = ['is_done', 'is_recal', 'has_pdf',  'ref_record', 'record', 'user', 'date', 'licence', 'cal_dev_1_cd',
                   'cal_dev_1_xd', 'cal_dev_2_cd', 'cal_dev_2_xd', 'cal_dev_3_cd', 'cal_dev_3_xd', 'cal_dev_4_cd', 'cal_dev_4_xd']


class suction_1_Form(forms.ModelForm):
    class Meta:
        model = Suction_1
        #fields = '__all__'
        exclude = ['is_done', 'is_recal', 'has_pdf',  'ref_record', 'record', 'user', 'date', 'licence', 'cal_dev_1_cd',
                   'cal_dev_1_xd', 'cal_dev_2_cd', 'cal_dev_2_xd', 'cal_dev_3_cd', 'cal_dev_3_xd', 'cal_dev_4_cd', 'cal_dev_4_xd']


class syringe_pump_1_Form(forms.ModelForm):
    class Meta:
        model = SyringePump_1
        #fields = '__all__'
        exclude = ['is_done', 'is_recal', 'has_pdf',  'ref_record', 'record', 'user', 'date', 'licence', 'cal_dev_1_cd',
                   'cal_dev_1_xd', 'cal_dev_2_cd', 'cal_dev_2_xd', 'cal_dev_3_cd', 'cal_dev_3_xd', 'cal_dev_4_cd', 'cal_dev_4_xd']


class electrocauter_1_Form(forms.ModelForm):
    class Meta:
        model = ElectroCauter_1
        #fields = '__all__'
        exclude = ['is_done', 'is_recal', 'has_pdf',  'ref_record', 'record', 'user', 'date', 'licence', 'cal_dev_1_cd', 'cal_dev_1_xd',
                   'cal_dev_2_cd', 'cal_dev_2_xd', 'cal_dev_3_cd', 'cal_dev_3_xd', 'cal_dev_4_cd', 'cal_dev_4_xd', 'cal_dev_5_cd', 'cal_dev_5_xd']


class ventilator_1_Form(forms.ModelForm):
    class Meta:
        model = Ventilator_1
        #fields = '__all__'
        exclude = ['is_done', 'is_recal', 'has_pdf',  'ref_record', 'record', 'user', 'date', 'licence', 'cal_dev_1_cd',
                   'cal_dev_1_xd', 'cal_dev_2_cd', 'cal_dev_2_xd', 'cal_dev_3_cd', 'cal_dev_3_xd', 'cal_dev_4_cd', 'cal_dev_4_xd']


class AutoClave_1_Form(forms.ModelForm):
    class Meta:
        model = AutoClave_1
        #fields = '__all__'
        exclude = ['is_done', 'is_recal', 'has_pdf',  'ref_record', 'record', 'user', 'date', 'licence', 'cal_dev_1_cd', 'cal_dev_1_xd',
                   'cal_dev_2_cd', 'cal_dev_2_xd', 'cal_dev_3_cd', 'cal_dev_3_xd', 'cal_dev_4_cd', 'cal_dev_4_xd', 'cal_dev_5_cd', 'cal_dev_5_xd']

