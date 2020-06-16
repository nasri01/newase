from django import forms

from .models import *


class add_device_Form(forms.ModelForm):
    class Meta:
        model = AllDevice
        fields = '__all__'

