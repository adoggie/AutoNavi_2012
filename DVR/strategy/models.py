#--coding:utf-8--
from django.db import models
from device.models import Vehicle
HOUR=(
      (1,1),
      (2,2),
      (3,3),
      (4,4),
      (5,5),
      (6,6),
      (7,7),
      (8,8),
      (9,9),
      (10,10),
      (11,11),
      (12,12),
      (13,13),
      (14,14),
      (15,15),
      (16,16),
      (17,17),
      (18,18),
      (19,19),
      (20,20),
      (21,21),
      (22,22),
      (23,23),
      (24,24),
      )
# Create your models here.
class Areagroup(models.Model):
    name = models.CharField(max_length=100) #组名称
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['id']
        
class Area(models.Model):
    name = models.CharField(verbose_name=u'区域名称',max_length=100)
    area_map = models.TextField(verbose_name=u'区域范围')
    area_gps = models.TextField(verbose_name=u'区域范围',null=True,blank=True)
    group = models.ForeignKey(Areagroup,verbose_name=u'区域组',null=True,blank=True)
    
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['id']    

class Strategy_group(models.Model):
    name = models.CharField(verbose_name=u'策略组名称',max_length=100) #组名称
    descri = models.TextField(verbose_name=u'描述',null=True,blank=True)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['id']
    
class Strategy(models.Model):
    name = models.CharField(verbose_name=u'策略名称',max_length=100)
    area = models.ForeignKey(Area,verbose_name=u'区域',)
    group = models.ForeignKey(Strategy_group,verbose_name=u'策略组',null=True,blank=True)
    begin_date = models.DateField(verbose_name=u'开始日期')
    end_date = models.DateField(verbose_name=u'结束日期')
    begin_h = models.IntegerField(verbose_name=u'开始时点',choices=HOUR)
    end_h = models.IntegerField(verbose_name=u'结束时点',choices=HOUR)
    vechicles_r = models.ManyToManyField(Vehicle,related_name='vechicle_strategy_r')
    
    