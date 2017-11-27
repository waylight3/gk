from django.contrib import admin
from all.models import *

class ManagerAdmin(admin.ModelAdmin):
	list_display = ('user', 'name', 'cell', 'charge')

class CctvAdmin(admin.ModelAdmin):
	list_display = ('name', 'start_date', 'manager')
	filter_horizontal = ('spots', )

class MetaAdmin(admin.ModelAdmin):
	list_display = ('name', 'video', 'cctv')

class RowAdmin(admin.ModelAdmin):
	list_display = ('meta', 'time_stamp', 'obj_id', 'size', 'xpos', 'ypos', 'speed', 'color')

class VideoAdmin(admin.ModelAdmin):
	list_display = ('name', 'ext', 'cctv')

class StatAdmin(admin.ModelAdmin):
	list_display = ('meta', 'length', 'rec_no', 'avg_size', 'avg_x', 'avg_y', 'avg_speed')

class SpotAdmin(admin.ModelAdmin):
	list_display = ('indoor_loc', 'floor_no', 'dep_name', 'address')

class NeighborAdmin(models.Model):
	list_display = ('name', 'spot1', 'spot2')

class SequenceAdmin(models.Model):
	list_display = ('pk')
	filter_horizontal = ('neighbors', )

admin.site.register(Manager, ManagerAdmin)
admin.site.register(Cctv, CctvAdmin)
admin.site.register(Meta, MetaAdmin)
admin.site.register(Row, RowAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Stat, StatAdmin)
admin.site.register(Spot, SpotAdmin)
admin.site.register(Neighbor)
admin.site.register(Sequence)