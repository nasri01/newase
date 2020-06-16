from django.contrib import admin

from .models import *

class HospitalAdmin(admin.ModelAdmin):
    list_display = ("name", "city")
admin.site.register(Hospital,HospitalAdmin)

class StateAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
admin.site.register(State,StateAdmin)

class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "state")
admin.site.register(City,CityAdmin)
admin.site.register(DeviceType)

class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "type")
admin.site.register(Device,DeviceAdmin)
admin.site.register(Country)

class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
admin.site.register(Company,CompanyAdmin)
admin.site.register(Section)
admin.site.register(CalDevice,DeviceAdmin)

class All_DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "hospital","section")
admin.site.register(AllDevice,All_DeviceAdmin)

admin.site.register(Request)
admin.site.register(Licence)



admin.site.register(AdExcelArg)


admin.site.register(Accessory)
admin.site.register(UserProfile)
admin.site.register(Record)



admin.site.register(Comment)
admin.site.register(AdTestType)
admin.site.register(AdTestType0)
admin.site.register(AdTestType1)
class status(admin.ModelAdmin):
    list_display = ("id", "status")
admin.site.register(AdReqStatus,status)
admin.site.register(AdAzStatus,status)

admin.site.register(AdAccStatus)
admin.site.register(Parameters)





