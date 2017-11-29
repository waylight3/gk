from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime
from all.models import *

class Manager(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length=32, default='이름')
    cell = models.CharField(max_length=32, default='연락처')
    charge = models.BooleanField(default=False) # True(최고관리자), False(일반관리자)

    def __str__(self):
        return '%s(%s)' % (self.user, self.name)

class Spot(models.Model):
    indoor_loc = models.CharField(max_length=128, default='주소')
    floor_no = models.CharField(max_length=128, default='주소')
    dep_name = models.CharField(max_length=128, default='주소')
    address = models.CharField(max_length=128, default='주소')

    def __str__(self):
        return '%s' % self.address

class Cctv(models.Model):
    name = models.CharField(max_length=128, default='이름')
    start_date = models.DateTimeField(default=datetime.now)
    manager = models.ForeignKey(Manager, blank=True, null=True, default=None, related_name='manager_cctvs')
    spots = models.ManyToManyField(Spot, blank=True, symmetrical=True, related_name='spot_cctvs')

    def __str__(self):
        return '%s' % self.name

class Video(models.Model):
    name = models.CharField(max_length=128, default='이름')
    ext = models.CharField(max_length=32, default='확장자')
    cctv = models.ForeignKey(Cctv, blank=True, null=True, default=None, related_name='cctv_videos')

    def __str__(self):
        return '%s(%s)' % (self.name, self.ext)

class Meta(models.Model):
    name = models.CharField(max_length=128, default='이름')
    cctv = models.ForeignKey(Cctv, blank=True, null=True, default=None, related_name='cctv_metas')
    video = models.OneToOneField(Video)

    def __str__(self):
        return '%s' % self.name

class Row(models.Model):
    meta = models.ForeignKey(Meta, blank=True, null=True, default=None, related_name='meta_rows')
    obj_id = models.CharField(max_length=128, default='개체 번호')
    time_stamp = models.DateTimeField(default=datetime.now)
    size = models.CharField(max_length=128, default='개체 크기')
    xpos = models.FloatField(default=0.0)
    ypos = models.FloatField(default=0.0)
    speed = models.FloatField(default=0.0)
    color = models.CharField(max_length=32, default='색상')

    def __str__(self):
        return '%s(%s)' % (self.meta.name, self.pk)

class Stat(models.Model):
    meta = models.OneToOneField(Meta)
    length = models.IntegerField(default=0)
    rec_no = models.IntegerField(default=0)
    avg_size = models.FloatField(default=0.0)
    avg_x = models.FloatField(default=0.0)
    avg_y = models.FloatField(default=0.0)
    avg_speed = models.FloatField(default=0.0)

    def __str__(self):
        return '%s' % self.meta.name

class Neighbor(models.Model):
    name = models.CharField(max_length=128, default='이름')
    spot1 = models.ForeignKey(Spot, blank=True, null=True, default=None, related_name='spot1_neighbors')
    spot2 = models.ForeignKey(Spot, blank=True, null=True, default=None, related_name='spot2_neighbors')

    def __str__(self):
        return '%s' % self.name

class Sequence(models.Model):
    neighbors = models.ManyToManyField(Neighbor, blank=True, symmetrical=True, related_name='neighbor_seqs')

    def __str__(self):
        return '%s' % self.pk