from django.contrib import admin
from scada.models import Inverter, Plant, Meter, Weather, SCB, SCBString

admin.site.register(Inverter)
admin.site.register(Plant)
admin.site.register(Meter)
admin.site.register(Weather)
admin.site.register(SCB)
admin.site.register(SCBString)

