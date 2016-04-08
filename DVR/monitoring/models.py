#--coding:utf-8--
from django.db import models
from device.models import Vehicle,Dtu
# Create your models here.

class GPS_LOG(models.Model):
    vehicle = models.ForeignKey(Vehicle,verbose_name=u'车辆',null=True,blank=True)
    dtu = models.ForeignKey(Dtu,verbose_name=u'设备',null=True,blank=True)
    lon = models.FloatField(verbose_name=u'经度',null=True,blank=True) #经度
    lat = models.FloatField(verbose_name=u'纬度',null=True,blank=True) #纬度
    time = models.DateTimeField(verbose_name=u'信息上传时间',null=True,blank=True) #信息上传时间
    timetick = models.IntegerField(verbose_name=u'GPS时钟',null=True,blank=True)
    speed = models.FloatField(verbose_name=u'速度',null=True,blank=True)
    direction = models.FloatField(verbose_name=u'方向',null=True,blank=True)
    acc = models.IntegerField(verbose_name=u'Acc',null=True,blank=True)
    gsm_status = models.IntegerField(verbose_name=u'GSM状态',null=True,blank=True)
    gps_status = models.IntegerField(verbose_name=u'GPS状态',null=True,blank=True)
    host_status = models.IntegerField(verbose_name=u'主机状态',null=True,blank=True)
    alarm_status = models.IntegerField(verbose_name=u'报警状态',null=True,blank=True)
    sd_index = models.IntegerField(verbose_name=u'sd_index',null=True,blank=True)
    av = models.IntegerField(verbose_name=u'Av',null=True,blank=True)
    lon_map = models.FloatField(verbose_name=u'地图经度',null=True,blank=True)
    lat_map = models.FloatField(verbose_name=u'地图纬度',null=True,blank=True)
    addr = models.TextField(verbose_name=u'实际地址',null=True,blank=True)
    
    def __unicode__(self):
        return  u'%s %s' % (self.vehicle, self.dtu)
    class Meta:
        db_table = 'gps_log'
        ordering = ['id']
        
