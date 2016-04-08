#--coding:utf-8--
from django.db import models
from system.models import User 

# Create your models here.
class Dtu(models.Model):
    dtu_num = models.CharField(verbose_name=u'DTU设备编号',max_length=100,unique=True)
    name = models.CharField(verbose_name=u'DTU设备名称',max_length=100)
    sim_id = models.CharField(verbose_name=u'SIM卡号',max_length=100,blank=True,unique=True)
    password = models.CharField(verbose_name=u'密码',max_length=100)
    ip_addr = models.CharField(verbose_name=u'IP地址',max_length=100)
    port = models.IntegerField(verbose_name=u'端口')
    interval = models.IntegerField(verbose_name=u'轮询时间')#轮询时间

    
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['id']

class Dtu_group(models.Model):
    name = models.CharField(verbose_name=u'DTU设备组名称',max_length=100) #组名称
    user = models.ForeignKey(User,verbose_name=u'所属用户')
    dtus = models.ManyToManyField(Dtu,through='Dtu_Group_r') 
           
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ["id"]
        unique_together = ("name", "user")
        
class Dtu_Group_r(models.Model):
    dtu = models.ForeignKey(Dtu,verbose_name=u'DTU设备')
    dtu_group = models.ForeignKey(Dtu_group,verbose_name=u'DTU设备组')
        
    def __unicode__(self):
        return  u'%s %s' % (self.dtu, self.dtu_group)
    class Meta:
        ordering = ['id']
        unique_together = ("dtu", "dtu_group")
    
        
class Dev_reg_log(models.Model):
    dtu = models.ForeignKey(Dtu,verbose_name=u'DTU设备')
    time = models.DateTimeField(verbose_name=u'DTU设备注册时间')
    status = models.BooleanField(verbose_name=u'DTU设备注册状态')
    reason = models.TextField(verbose_name=u'DTU设备注册失败原因')
    password = models.CharField(max_length=100,verbose_name=u'DTU设备提交密码')  #DTU设备上传的密码
    
    def __unicode__(self):
        return self.dtu
    class Meta:
        db_table = 'dev_reg_log'
        ordering = ['id']    



'''
车辆表,存储车辆的基本信息
'''
class Vehicle(models.Model):
    vehicle_num = models.CharField(verbose_name=u'车辆编号',max_length=100,unique=True)
    name = models.CharField(verbose_name=u'车辆名称',max_length=100)
    driver = models.CharField(verbose_name=u'联系人',max_length=100,blank=True)
    tel = models.CharField(verbose_name=u'联系方式',max_length=100,blank=True)
    descri = models.TextField(verbose_name=u'描述',blank=True,null=True)
    install_date = models.DateField(verbose_name=u'DTU设备安装日期',blank=True,null=True)
    status = models.IntegerField(verbose_name=u'DTU设备状态',blank=True,null=True)
    dtu = models.OneToOneField(Dtu,verbose_name=u'DTU设备',blank=True,null=True)  #车跟DTU设备一对一关系
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['id']
        
class Vehicle_group(models.Model):
    name = models.CharField(verbose_name=u'车辆组名称',max_length=100) #组名称
    user = models.ForeignKey(User,verbose_name=u'所属用户',)
    vehicles = models.ManyToManyField(Vehicle,through='Vehicle_Group_r')        
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['id']
        unique_together = ("name", "user")

class Vehicle_Group_r(models.Model):
    vehicle = models.ForeignKey(Vehicle,verbose_name=u'车辆')
    vehicle_group = models.ForeignKey(Vehicle_group,verbose_name=u'车辆组')
        
    def __unicode__(self):
        return  u'%s %s' % (self.vehicle, self.vehicle_group)
    class Meta:
        ordering = ['id']
        unique_together = ("vehicle", "vehicle_group")            
