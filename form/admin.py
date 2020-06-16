from django.contrib import admin

from .models import *


class formAdmin(admin.ModelAdmin):
    list_display = ("__str__", "has_pdf", "licence", "is_recal", "is_done",
                    "status", "date", "request", "device", "user", )


admin.site.register(MonitorSpo2_1, formAdmin)
admin.site.register(MonitorECG_1, formAdmin)
admin.site.register(MonitorNIBP_1, formAdmin)
admin.site.register(MonitorSafety_1, formAdmin)

admin.site.register(AED_1, formAdmin)
admin.site.register(AnesthesiaMachine_1, formAdmin)
admin.site.register(Defibrilator_1, formAdmin)
admin.site.register(ECG_1, formAdmin)
admin.site.register(FlowMeter_1, formAdmin)
admin.site.register(InfusionPump_1, formAdmin)
admin.site.register(ManoMeter_1, formAdmin)
admin.site.register(ElectroCauter_1, formAdmin)
admin.site.register(Spo2_1, formAdmin)
admin.site.register(SyringePump_1, formAdmin)
admin.site.register(Suction_1, formAdmin)
admin.site.register(Ventilator_1, formAdmin)
admin.site.register(CantTest)
